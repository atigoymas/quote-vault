from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.database import DbSession
from app.models import Quote
from app.schemas import QuoteCreate, QuoteOut

router = APIRouter(tags=["quotes"])


@router.post("/quotes", response_model=QuoteOut, status_code=201)
async def create_quote(payload: QuoteCreate, db: DbSession) -> Quote:
    quote = Quote(text=payload.text, source=payload.source, author=payload.author)
    db.add(quote)
    await db.commit()
    await db.refresh(quote)
    return quote


@router.get("/quotes", response_model=list[QuoteOut])
async def list_quotes(
    db: DbSession,
    tag: str | None = None,
    limit: int = 50,
    offset: int = 0,
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
