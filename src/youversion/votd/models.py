"""Verse of the Day models."""

from pydantic import BaseModel


class VerseOfTheDay(BaseModel):
    """Verse of the Day entry."""

    day: int  # 1-366
    passage_id: str
