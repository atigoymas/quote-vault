from httpx import AsyncClient

from app import rate_limit

STRANGER_HEADERS = {"X-Owner-Key": "wrong-key"}


async def test_quotes_endpoint_returns_429_after_threshold_for_non_owner(
    client: AsyncClient,
) -> None:
    for _ in range(rate_limit.PUBLIC_MAX_REQUESTS_PER_WINDOW):
        response = await client.post(
            "/quotes", json={"text": "filler quote"}, headers=STRANGER_HEADERS
        )
        assert response.status_code == 201

    response = await client.post(
        "/quotes", json={"text": "one too many"}, headers=STRANGER_HEADERS
    )

    assert response.status_code == 429


async def test_owner_key_bypasses_rate_limit(client: AsyncClient) -> None:
    # the shared `client` fixture already sends the correct owner key
    for _ in range(rate_limit.PUBLIC_MAX_REQUESTS_PER_WINDOW + 5):
        response = await client.post("/quotes", json={"text": "filler quote"})
        assert response.status_code == 201


async def test_rate_limit_is_shared_across_gemini_routes_for_non_owner(
    client: AsyncClient,
) -> None:
    for _ in range(rate_limit.PUBLIC_MAX_REQUESTS_PER_WINDOW):
        response = await client.post(
            "/quotes", json={"text": "filler quote"}, headers=STRANGER_HEADERS
        )
        assert response.status_code == 201

    response = await client.post(
        "/search/mood", json={"feeling": "anything"}, headers=STRANGER_HEADERS
    )

    assert response.status_code == 429


async def test_unrelated_endpoints_are_not_rate_limited(client: AsyncClient) -> None:
    for _ in range(rate_limit.PUBLIC_MAX_REQUESTS_PER_WINDOW + 5):
        response = await client.get("/tags", headers=STRANGER_HEADERS)
        assert response.status_code == 200


async def test_owner_check_reports_true_for_correct_key(client: AsyncClient) -> None:
    response = await client.get("/owner/check")

    assert response.status_code == 200
    assert response.json() == {"is_owner": True}


async def test_owner_check_reports_false_for_wrong_key(client: AsyncClient) -> None:
    response = await client.get("/owner/check", headers=STRANGER_HEADERS)

    assert response.status_code == 200
    assert response.json() == {"is_owner": False}
