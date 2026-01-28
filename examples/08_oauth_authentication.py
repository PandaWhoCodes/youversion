#!/usr/bin/env python3
"""OAuth authentication with YouVersion API using PKCE flow.

This example demonstrates how to:
1. Start a local HTTP server to receive the OAuth callback
2. Generate PKCE code verifier and challenge
3. Open the browser for user authentication
4. Exchange the authorization code for JWT tokens
5. Use the access token to make authenticated API calls

Usage:
    python examples/08_oauth_authentication.py

Requirements:
    - YOUVERSION_CLIENT_ID environment variable (your app's client ID from Platform Portal)
    - A registered redirect URI of http://localhost:8080/callback in your app settings
"""

import base64
import hashlib
import http.server
import os
import secrets
import socketserver
import threading
import urllib.parse
import webbrowser
from dataclasses import dataclass

import httpx

# Configuration
CLIENT_ID = os.environ.get("YOUVERSION_CLIENT_ID", "your-client-id")
REDIRECT_URI = "http://localhost:8080/callback"
AUTH_BASE_URL = "https://api.youversion.com/auth"
SCOPES = "openid profile email"


@dataclass
class TokenResponse:
    """OAuth token response."""

    access_token: str
    id_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler to capture OAuth callback."""

    auth_code: str | None = None
    user_data: dict[str, str] | None = None
    error: str | None = None

    def do_GET(self) -> None:
        """Handle GET request from OAuth callback."""
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/callback":
            query = urllib.parse.parse_qs(parsed.query)

            # Check for error
            if "error" in query:
                OAuthCallbackHandler.error = query.get("error", ["Unknown error"])[0]
                self._send_response("Authentication failed. You can close this window.")
                return

            # Capture user data from callback
            OAuthCallbackHandler.user_data = {
                "yvp_id": query.get("yvp_id", [""])[0],
                "user_name": query.get("user_name", [""])[0],
                "user_email": query.get("user_email", [""])[0],
                "profile_picture": query.get("profile_picture", [""])[0],
            }

            self._send_response(
                "Authentication successful! You can close this window and return to the terminal."
            )
        else:
            self.send_error(404)

    def _send_response(self, message: str) -> None:
        """Send HTML response."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>YouVersion OAuth</title></head>
        <body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1>{message}</h1>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def log_message(self, format: str, *args: object) -> None:
        """Suppress default logging."""
        pass


def generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code verifier and challenge.

    Returns:
        Tuple of (code_verifier, code_challenge)
    """
    # Generate random code verifier (43-128 characters)
    code_verifier = secrets.token_urlsafe(32)

    # Create SHA256 hash and base64url encode it
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

    return code_verifier, code_challenge


def start_callback_server(port: int = 8080) -> socketserver.TCPServer:
    """Start local HTTP server to receive OAuth callback.

    Args:
        port: Port to listen on (default: 8080)

    Returns:
        The running server instance
    """
    server = socketserver.TCPServer(("", port), OAuthCallbackHandler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    return server


def build_authorization_url(client_id: str, code_challenge: str, state: str) -> str:
    """Build the authorization URL for user login.

    Args:
        client_id: Your app's client ID
        code_challenge: PKCE code challenge
        state: Random state for CSRF protection

    Returns:
        Full authorization URL
    """
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
        "nonce": secrets.token_urlsafe(16),
    }
    return f"{AUTH_BASE_URL}/authorize?" + urllib.parse.urlencode(params)


def exchange_code_for_tokens(
    auth_code: str, code_verifier: str, client_id: str
) -> TokenResponse:
    """Exchange authorization code for access tokens.

    Args:
        auth_code: Authorization code from callback
        code_verifier: PKCE code verifier
        client_id: Your app's client ID

    Returns:
        TokenResponse with access_token, id_token, refresh_token
    """
    with httpx.Client() as client:
        response = client.post(
            f"{AUTH_BASE_URL}/token",
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": REDIRECT_URI,
                "client_id": client_id,
                "code_verifier": code_verifier,
            },
        )
        response.raise_for_status()
        data = response.json()

        return TokenResponse(
            access_token=data["access_token"],
            id_token=data["id_token"],
            refresh_token=data["refresh_token"],
            token_type=data.get("token_type", "Bearer"),
            expires_in=data.get("expires_in", 3600),
        )


def get_auth_code_from_callback(user_data: dict[str, str], client_id: str) -> str:
    """Post user data to callback endpoint to get authorization code.

    Args:
        user_data: User data received from authorize redirect
        client_id: Your app's client ID

    Returns:
        Authorization code
    """
    with httpx.Client() as client:
        response = client.post(
            f"{AUTH_BASE_URL}/callback",
            json={
                "client_id": client_id,
                "redirect_uri": REDIRECT_URI,
                **user_data,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["code"]


def authenticate() -> TokenResponse | None:
    """Run the full OAuth PKCE authentication flow.

    Returns:
        TokenResponse if successful, None if failed
    """
    print("=" * 60)
    print("YouVersion OAuth Authentication (PKCE Flow)")
    print("=" * 60)

    # Generate PKCE pair
    code_verifier, code_challenge = generate_pkce_pair()
    state = secrets.token_urlsafe(16)

    print("\n1. Starting local callback server on http://localhost:8080...")
    server = start_callback_server()

    # Build and open authorization URL
    auth_url = build_authorization_url(CLIENT_ID, code_challenge, state)
    print("\n2. Opening browser for authentication...")
    print(f"   URL: {auth_url[:80]}...")
    webbrowser.open(auth_url)

    print("\n3. Waiting for callback (complete login in browser)...")

    # Wait for callback
    import time

    timeout = 120  # 2 minutes
    start = time.time()
    while OAuthCallbackHandler.user_data is None and OAuthCallbackHandler.error is None:
        if time.time() - start > timeout:
            print("   Timeout waiting for callback")
            server.server_close()
            return None
        time.sleep(0.5)

    server.server_close()

    if OAuthCallbackHandler.error:
        print(f"   Error: {OAuthCallbackHandler.error}")
        return None

    user_data = OAuthCallbackHandler.user_data
    if user_data is None:
        print("   Error: No user data received")
        return None
    print(f"   Received callback for user: {user_data.get('user_name', 'Unknown')}")

    # Exchange for tokens
    print("\n4. Exchanging authorization code for tokens...")
    try:
        auth_code = get_auth_code_from_callback(user_data, CLIENT_ID)
        tokens = exchange_code_for_tokens(auth_code, code_verifier, CLIENT_ID)
        print("   Success! Tokens received.")
        print(f"   Access token expires in: {tokens.expires_in} seconds")
        return tokens
    except httpx.HTTPStatusError as e:
        print(f"   Error exchanging code: {e}")
        return None


if __name__ == "__main__":
    if CLIENT_ID == "your-client-id":
        print("Please set YOUVERSION_CLIENT_ID environment variable")
        print("Get your client ID from: https://developers.youversion.com")
        exit(1)

    tokens = authenticate()

    if tokens:
        print("\n" + "=" * 60)
        print("Authentication Complete!")
        print("=" * 60)
        print(f"\nAccess Token (first 50 chars): {tokens.access_token[:50]}...")
        print(f"Token Type: {tokens.token_type}")
        print(f"Expires In: {tokens.expires_in} seconds")
        print("\nYou can now use this access_token for authenticated API calls.")
        print("Set it as: export YOUVERSION_ACCESS_TOKEN='...'")
