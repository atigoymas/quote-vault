import math

from httpx import AsyncClient
from sqlalchemy import select

from app.database import async_session
from app.models import Quote


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)


async def test_embedding_similarity_ordering(client: AsyncClient) -> None:
    quotes = {
        "mortality_a": "The unexamined life is not worth living.",
        "mortality_b": "Know thyself, for the unreflective life is no life "
        "for a human being to live.",
        "unrelated": "Add two cups of flour and a pinch of salt to the mixing bowl.",
    }
    for text in quotes.values():
        response = await client.post("/quotes", json={"text": text})
        assert response.status_code == 201

    async with async_session() as session:
        result = await session.execute(select(Quote).order_by(Quote.id))
        rows = result.scalars().all()
        stored = {key: quote.embedding for key, quote in zip(quotes, rows, strict=True)}

    similar_pair = _cosine_similarity(stored["mortality_a"], stored["mortality_b"])
    unrelated_pair_a = _cosine_similarity(stored["mortality_a"], stored["unrelated"])
    unrelated_pair_b = _cosine_similarity(stored["mortality_b"], stored["unrelated"])

    assert similar_pair > unrelated_pair_a
    assert similar_pair > unrelated_pair_b
