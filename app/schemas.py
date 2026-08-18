from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QuoteCreate(BaseModel):
    text: str
    source: str | None = None
    author: str | None = None


class QuoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    source: str | None
    author: str | None
    tags: list[str] | None
    created_at: datetime


class TagCount(BaseModel):
    tag: str
    count: int


class TopicSearchRequest(BaseModel):
    query: str
    tag: str | None = None
    limit: int = 5


class SearchResult(BaseModel):
    id: int
    text: str
    source: str | None
    author: str | None
    tags: list[str] | None
    similarity: float


class MoodSearchRequest(BaseModel):
    feeling: str
    tag: str | None = None


class MoodSearchResult(SearchResult):
    explanation: str | None
