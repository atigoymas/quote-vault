from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class QuoteCreate(BaseModel):
    text: str = Field(max_length=4000)
    source: str | None = Field(default=None, max_length=200)
    author: str | None = Field(default=None, max_length=200)


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
    query: str = Field(max_length=500)
    tag: str | None = None
    limit: int = Field(default=5, gt=0, le=50)


class SearchResult(BaseModel):
    id: int
    text: str
    source: str | None
    author: str | None
    tags: list[str] | None
    similarity: float


class MoodSearchRequest(BaseModel):
    feeling: str = Field(max_length=500)
    tag: str | None = None


class MoodSearchResult(SearchResult):
    explanation: str | None
