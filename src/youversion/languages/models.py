"""Language models."""

from pydantic import BaseModel


class Language(BaseModel):
    """A language supported by YouVersion."""

    id: str  # BCP 47 tag
    language: str  # ISO 639
    script: str | None = None
    script_name: str | None = None
    aliases: list[str] = []
    display_names: dict[str, str] = {}
    scripts: list[str] = []
    variants: list[str] = []
    countries: list[str] = []
    text_direction: str  # "ltr" or "rtl"
    writing_population: int = 0
    speaking_population: int = 0
    default_bible_id: int | None = None
