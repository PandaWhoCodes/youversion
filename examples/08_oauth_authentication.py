#!/usr/bin/env python3
"""YouVersion OAuth Sign-In - Simple 2-step authentication flow.

Based on: https://developers.youversion.com/sign-in-apis

Flow:
1. User visits authorize URL → logs in at login.youversion.com → redirects back
   with user data (yvp_id, user_name, user_email, profile_picture) as query params
2. Post user data to /auth/callback → get auth code → exchange for JWT tokens

Usage:
    export YOUVERSION_CLIENT_ID="your-client-id"
    python examples/08_oauth_authentication.py

Get your client_id from: https://developers.youversion.com (Platform Portal)
"""

import base64
import hashlib
import http.server
import secrets
import socketserver
import threading
import urllib.parse
import webbrowser
from dataclasses import dataclass
from typing import Any

import httpx

# Configuration - get client_id from Platform Portal
CLIENT_ID = "your-client-id"  # Replace with your client_id or set via env
REDIRECT_URI = "http://localhost:8080/callback"
AUTH_BASE_URL = "https://api.youversion.com/auth"


@dataclass
class UserInfo:
    """User information from YouVersion sign-in."""

    yvp_id: str
    user_name: str
    user_email: str
    profile_picture: str


@dataclass
class Tokens:
    """JWT tokens from authentication."""

    access_token: str
    id_token: str
    refresh_token: str
    expires_in: int


class CallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Simple HTTP handler to capture the OAuth callback."""

    user_info: UserInfo | None = None
    error: str | None = None
    received: threading.Event = threading.Event()

    def do_GET(self) -> None:
        """Handle GET request - capture user data from callback."""
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path != "/callback":
            self.send_error(404)
            return

        query = urllib.parse.parse_qs(parsed.query)

        # Check for error
        if "error" in query:
            CallbackHandler.error = query.get("error", ["Unknown"])[0]
            self._respond("Authentication failed. Check terminal.")
            CallbackHandler.received.set()
            return

        # Extract user data from query params
        CallbackHandler.user_info = UserInfo(
            yvp_id=query.get("yvp_id", [""])[0],
            user_name=query.get("user_name", [""])[0],
            user_email=query.get("user_email", [""])[0],
            profile_picture=query.get("profile_picture", [""])[0],
        )

        self._respond("Success! You can close this tab.")
        CallbackHandler.received.set()

    def _respond(self, message: str) -> None:
        """Send simple HTML response."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = f"<html><body style='font-family:sans-serif;text-align:center;padding:50px'><h2>{message}</h2></body></html>"
        self.wfile.write(html.encode())

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress logging."""
        pass


def generate_pkce() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge."""
    verifier = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()
    return verifier, challenge


def build_auth_url(client_id: str, code_challenge: str, state: str) -> str:
    """Build the authorization URL."""
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": "openid profile email",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
        "nonce": secrets.token_urlsafe(16),
    }
    return f"{AUTH_BASE_URL}/authorize?" + urllib.parse.urlencode(params)


def exchange_for_tokens(
    user_info: UserInfo, code_verifier: str, client_id: str
) -> Tokens:
    """
    Step 2: Exchange user data for tokens.

    1. Post user data to /auth/callback to get authorization code
    2. Exchange code for JWT tokens
    """
    with httpx.Client() as http:
        # Step 2a: Post user data to get auth code
        callback_resp = http.post(
            f"{AUTH_BASE_URL}/callback",
            json={
                "client_id": client_id,
                "redirect_uri": REDIRECT_URI,
                "yvp_id": user_info.yvp_id,
                "user_name": user_info.user_name,
                "user_email": user_info.user_email,
                "profile_picture": user_info.profile_picture,
            },
        )
        callback_resp.raise_for_status()
        auth_code = callback_resp.json()["code"]

        # Step 2b: Exchange code for tokens
        token_resp = http.post(
            f"{AUTH_BASE_URL}/token",
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": REDIRECT_URI,
                "client_id": client_id,
                "code_verifier": code_verifier,
            },
        )
        token_resp.raise_for_status()
        data = token_resp.json()

        return Tokens(
            access_token=data["access_token"],
            id_token=data["id_token"],
            refresh_token=data["refresh_token"],
            expires_in=data.get("expires_in", 3600),
        )


def run_auth_flow(client_id: str) -> tuple[UserInfo, Tokens] | None:
    """
    Run the complete 2-step authentication flow.

    Step 1: User logs in via browser → we receive user info
    Step 2: Exchange user info for JWT tokens

    Returns (UserInfo, Tokens) on success, None on failure.
    """
    # Reset state
    CallbackHandler.user_info = None
    CallbackHandler.error = None
    CallbackHandler.received = threading.Event()

    # Generate PKCE
    code_verifier, code_challenge = generate_pkce()
    state = secrets.token_urlsafe(16)

    # Start callback server
    print("\n[Step 1] Starting local server on http://localhost:8080...")
    server = socketserver.TCPServer(("", 8080), CallbackHandler)
    server_thread = threading.Thread(target=server.handle_request, daemon=True)
    server_thread.start()

    # Open browser for login
    auth_url = build_auth_url(client_id, code_challenge, state)
    print("[Step 1] Opening browser for YouVersion sign-in...")
    webbrowser.open(auth_url)

    # Wait for callback (timeout 2 minutes)
    print("[Step 1] Waiting for sign-in (complete in browser)...")
    if not CallbackHandler.received.wait(timeout=120):
        print("Timeout waiting for callback")
        server.server_close()
        return None

    server.server_close()

    if CallbackHandler.error:
        print(f"Error: {CallbackHandler.error}")
        return None

    user_info = CallbackHandler.user_info
    if not user_info:
        print("No user info received")
        return None

    print(f"[Step 1] Got user info: {user_info.user_name} ({user_info.user_email})")

    # Exchange for tokens
    print("\n[Step 2] Exchanging for JWT tokens...")
    try:
        tokens = exchange_for_tokens(user_info, code_verifier, client_id)
        print("[Step 2] Success! Tokens received.")
        return user_info, tokens
    except httpx.HTTPStatusError as e:
        print(f"Error: {e}")
        return None


def main() -> None:
    """Main entry point."""
    import os

    client_id = os.environ.get("YOUVERSION_CLIENT_ID", CLIENT_ID)

    if client_id == "your-client-id":
        print("=" * 60)
        print("YouVersion OAuth Sign-In")
        print("=" * 60)
        print("\nPlease set your client_id:")
        print("  export YOUVERSION_CLIENT_ID='your-client-id'")
        print("\nGet it from: https://developers.youversion.com")
        return

    print("=" * 60)
    print("YouVersion OAuth Sign-In (2-Step Flow)")
    print("=" * 60)

    result = run_auth_flow(client_id)

    if result:
        user_info, tokens = result

        print("\n" + "=" * 60)
        print("Authentication Complete!")
        print("=" * 60)

        print("\nUser Info:")
        print(f"  YVP ID:   {user_info.yvp_id}")
        print(f"  Name:     {user_info.user_name}")
        print(f"  Email:    {user_info.user_email}")
        print(f"  Picture:  {user_info.profile_picture[:50]}..." if user_info.profile_picture else "  Picture:  (none)")

        print("\nTokens:")
        print(f"  Access:   {tokens.access_token[:40]}...")
        print(f"  Expires:  {tokens.expires_in} seconds")

        print("\nTo use the access token:")
        print(f"  export YOUVERSION_ACCESS_TOKEN='{tokens.access_token}'")
    else:
        print("\nAuthentication failed.")


if __name__ == "__main__":
    main()
