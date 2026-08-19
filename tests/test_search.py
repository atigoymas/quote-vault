import pytest
from httpx import AsyncClient

MORTALITY_A = "The unexamined life is not worth living."
MORTALITY_B = "Know thyself, for the unreflective life is no life for a human being to live."
UNRELATED = "Add two cups of flour and a pinch of salt to the mixing bowl."


async def test_search_topic_orders_by_similarity(client: AsyncClient) -> None:
    for text in (MORTALITY_A, MORTALITY_B, UNRELATED):
        await client.post("/quotes", json={"text": text})

    response = await client.post("/search/topic", json={"query": "reflecting on how to live"})

    assert response.status_code == 200
    body = response.json()
    texts_in_order = [row["text"] for row in body]
    assert texts_in_order.index(MORTALITY_A) < texts_in_order.index(UNRELATED)
    assert texts_in_order.index(MORTALITY_B) < texts_in_order.index(UNRELATED)
    similarities = [row["similarity"] for row in body]
    assert similarities == sorted(similarities, reverse=True)


async def test_search_topic_filters_by_tag(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    tags_by_text = {MORTALITY_A: ["philosophy"], MORTALITY_B: ["untagged"]}

    async def _fake_generate_tags(text: str, existing_tags: list[str] | None = None) -> list[str]:
        return tags_by_text[text]

    monkeypatch.setattr("app.routers.quotes.generate_tags", _fake_generate_tags)
    for text in tags_by_text:
        await client.post("/quotes", json={"text": text})

    response = await client.post(
        "/search/topic", json={"query": "reflecting on how to live", "tag": "philosophy"}
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["text"] == MORTALITY_A


async def test_search_mood_returns_best_match(client: AsyncClient) -> None:
    for text in (MORTALITY_A, UNRELATED):
        await client.post("/quotes", json={"text": text})

    response = await client.post("/search/mood", json={"feeling": "questioning how I'm living"})

    assert response.status_code == 200
    assert response.json()["text"] == MORTALITY_A


async def test_search_mood_includes_llm_explanation(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _fake_explanation(feeling: str, quote_text: str) -> str:
        return "It speaks to your search for self-understanding."

    monkeypatch.setattr("app.routers.search.generate_explanation", _fake_explanation)
    await client.post("/quotes", json={"text": MORTALITY_A})

    response = await client.post("/search/mood", json={"feeling": "questioning how I'm living"})

    assert response.status_code == 200
    assert response.json()["explanation"] == "It speaks to your search for self-understanding."


async def test_search_mood_explanation_failure_does_not_block_result(
    client: AsyncClient,
) -> None:
    await client.post("/quotes", json={"text": MORTALITY_A})

    response = await client.post("/search/mood", json={"feeling": "questioning how I'm living"})

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == MORTALITY_A
    assert body["explanation"] is None


async def test_search_mood_falls_back_to_tag_based_explanation_when_llm_fails(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _fake_generate_tags(text: str, existing_tags: list[str] | None = None) -> list[str]:
        return ["introspection", "purpose"]

    monkeypatch.setattr("app.routers.quotes.generate_tags", _fake_generate_tags)
    await client.post("/quotes", json={"text": MORTALITY_A})

    response = await client.post("/search/mood", json={"feeling": "questioning how I'm living"})

    assert response.status_code == 200
    body = response.json()
    assert body["explanation"] is not None
    assert "introspection" in body["explanation"]


async def test_search_mood_filters_by_tag(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    tags_by_text = {MORTALITY_A: ["untagged"], UNRELATED: ["cooking"]}

    async def _fake_generate_tags(text: str, existing_tags: list[str] | None = None) -> list[str]:
        return tags_by_text[text]

    monkeypatch.setattr("app.routers.quotes.generate_tags", _fake_generate_tags)
    for text in tags_by_text:
        await client.post("/quotes", json={"text": text})

    response = await client.post(
        "/search/mood", json={"feeling": "questioning how I'm living", "tag": "cooking"}
    )

    assert response.status_code == 200
    assert response.json()["text"] == UNRELATED


async def test_search_mood_no_quotes_returns_404(client: AsyncClient) -> None:
    response = await client.post("/search/mood", json={"feeling": "anything"})

    assert response.status_code == 404
