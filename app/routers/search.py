import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Select, select

from app.database import DbSession
from app.embeddings import embed_text
from app.models import Quote
from app.rate_limit import enforce_rate_limit
from app.schemas import (
    MoodSearchRequest,
    MoodSearchResult,
    SearchResult,
    TopicSearchRequest,
)
from app.tagging import fallback_explanation, generate_explanation

router = APIRouter(tags=["search"])


def _ranked_query(embedding: list[float], tag: str | None, limit: int) -> Select:
    distance = Quote.embedding.cosine_distance(embedding)
    stmt = select(Quote, (1 - distance).label("similarity")).order_by(distance).limit(limit)
    if tag is not None:
        stmt = stmt.where(Quote.tags.any(tag))
    return stmt


def _to_search_result(quote: Quote, similarity: float) -> SearchResult:
    return SearchResult(
        id=quote.id,
        text=quote.text,
        source=quote.source,
        author=quote.author,
        tags=quote.tags,
        similarity=similarity,
    )


@router.post("/search/topic", response_model=list[SearchResult])
async def search_topic(payload: TopicSearchRequest, db: DbSession) -> list[SearchResult]:
    embedding = await asyncio.to_thread(embed_text, payload.query)
    result = await db.execute(_ranked_query(embedding, payload.tag, payload.limit))
    return [_to_search_result(quote, similarity) for quote, similarity in result.all()]


@router.post(
    "/search/mood",
    response_model=MoodSearchResult,
    dependencies=[Depends(enforce_rate_limit)],
)
async def search_mood(payload: MoodSearchRequest, db: DbSession) -> MoodSearchResult:
    embedding = await asyncio.to_thread(embed_text, payload.feeling)
    result = await db.execute(_ranked_query(embedding, payload.tag, limit=1))
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="No quotes match that mood yet")

    quote, similarity = row
    explanation = await generate_explanation(payload.feeling, quote.text)
    if explanation is None:
        explanation = fallback_explanation(payload.feeling, quote.tags)
    result = _to_search_result(quote, similarity)
    return MoodSearchResult(**result.model_dump(), explanation=explanation)
