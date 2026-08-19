from httpx import AsyncClient

from app.rate_limit import MAX_REQUESTS_PER_WINDOW


async def test_quotes_endpoint_returns_429_after_threshold(client: AsyncClient) -> None:
    for _ in range(MAX_REQUESTS_PER_WINDOW):
        response = await client.post("/quotes", json={"text": "filler quote"})
        assert response.status_code == 201

    response = await client.post("/quotes", json={"text": "one too many"})

    assert response.status_code == 429


async def test_rate_limit_is_shared_across_gemini_routes(client: AsyncClient) -> None:
    for _ in range(MAX_REQUESTS_PER_WINDOW):
        response = await client.post("/quotes", json={"text": "filler quote"})
        assert response.status_code == 201

    response = await client.post("/search/mood", json={"feeling": "anything"})

    assert response.status_code == 429


async def test_unrelated_endpoints_are_not_rate_limited(client: AsyncClient) -> None:
    for _ in range(MAX_REQUESTS_PER_WINDOW + 5):
        response = await client.get("/tags")
        assert response.status_code == 200
