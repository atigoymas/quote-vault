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
