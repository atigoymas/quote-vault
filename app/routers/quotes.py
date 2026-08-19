import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import DbSession
from app.embeddings import embed_text
from app.models import Quote
from app.rate_limit import require_owner
from app.schemas import QuoteCreate, QuoteOut, TagCount
from app.tagging import generate_tags

router = APIRouter(tags=["quotes"])


async def _distinct_tags(db: AsyncSession) -> list[str]:
    result = await db.execute(
        sql_text("SELECT DISTINCT tag FROM quotes, LATERAL unnest(tags) AS tag")
    )
    return [row.tag for row in result]


@router.post(
    "/quotes",
    response_model=QuoteOut,
    status_code=201,
    dependencies=[Depends(require_owner)],
)
async def create_quote(payload: QuoteCreate, db: DbSession) -> Quote:
    embedding = await asyncio.to_thread(embed_text, payload.text)
    existing_tags = await _distinct_tags(db)
    tags = await generate_tags(payload.text, existing_tags)
    quote = Quote(
        text=payload.text,
        source=payload.source,
        author=payload.author,
        embedding=embedding,
        tags=tags or None,
    )
    db.add(quote)
    await db.commit()
    await db.refresh(quote)
    return quote


@router.get("/quotes", response_model=list[QuoteOut])
async def list_quotes(
    db: DbSession,
    tag: str | None = None,
    limit: int = Query(default=50, gt=0, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Quote]:
    stmt = select(Quote).order_by(Quote.created_at.desc()).limit(limit).offset(offset)
    if tag is not None:
        stmt = stmt.where(Quote.tags.any(tag))
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/quotes/{quote_id}", response_model=QuoteOut)
async def get_quote(quote_id: int, db: DbSession) -> Quote:
    quote = await db.get(Quote, quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote


@router.get("/tags", response_model=list[TagCount])
async def list_tags(db: DbSession) -> list[TagCount]:
    result = await db.execute(
        sql_text(
            "SELECT tag, COUNT(*) AS count FROM quotes, LATERAL unnest(tags) AS tag "
            "GROUP BY tag ORDER BY count DESC, tag ASC"
        )
    )
    return [TagCount(tag=row.tag, count=row.count) for row in result]
