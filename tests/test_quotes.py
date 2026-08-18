import pytest
from httpx import AsyncClient


async def test_create_quote(client: AsyncClient) -> None:
    response = await client.post(
        "/quotes",
        json={"text": "The unexamined life is not worth living.", "author": "Socrates"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["text"] == "The unexamined life is not worth living."
    assert body["author"] == "Socrates"
    assert body["tags"] is None


async def test_list_quotes(client: AsyncClient) -> None:
    await client.post("/quotes", json={"text": "Quote one"})
    await client.post("/quotes", json={"text": "Quote two"})

    response = await client.get("/quotes")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {q["text"] for q in body} == {"Quote one", "Quote two"}


async def test_get_quote_not_found(client: AsyncClient) -> None:
    response = await client.get("/quotes/999")
    assert response.status_code == 404


async def test_list_quotes_filtered_by_tag(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    tags_by_text = {
        "Quote about hope": ["hope", "resilience"],
        "Quote about grief": ["grief", "loss"],
    }

    async def _fake_generate_tags(text: str, existing_tags: list[str] | None = None) -> list[str]:
        return tags_by_text[text]

    monkeypatch.setattr("app.routers.quotes.generate_tags", _fake_generate_tags)
    for text in tags_by_text:
        await client.post("/quotes", json={"text": text})

    response = await client.get("/quotes", params={"tag": "hope"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["text"] == "Quote about hope"


async def test_list_tags_returns_counts(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    tags_by_text = {
        "Quote one": ["hope", "resilience"],
        "Quote two": ["hope"],
        "Quote three": ["grief"],
    }

    async def _fake_generate_tags(text: str, existing_tags: list[str] | None = None) -> list[str]:
        return tags_by_text[text]

    monkeypatch.setattr("app.routers.quotes.generate_tags", _fake_generate_tags)
    for text in tags_by_text:
        await client.post("/quotes", json={"text": text})

    response = await client.get("/tags")

    assert response.status_code == 200
    counts = {row["tag"]: row["count"] for row in response.json()}
    assert counts == {"hope": 2, "resilience": 1, "grief": 1}
