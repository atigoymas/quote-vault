import json
from types import SimpleNamespace

import pytest
from httpx import AsyncClient

from app import tagging


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


def _fake_client(response_text: str) -> SimpleNamespace:
    def generate_content(*, model: str, contents: str, config: object) -> _FakeResponse:
        return _FakeResponse(response_text)

    return SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))


def test_generate_tags_sync_parses_valid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        tagging,
        "_client",
        lambda api_key: _fake_client(json.dumps(["longing", "solitude", "resolve"])),
    )

    tags = tagging._generate_tags_sync("some quote", api_key="fake-key")

    assert tags == ["longing", "solitude", "resolve"]


def test_generate_tags_sync_handles_malformed_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tagging, "_client", lambda api_key: _fake_client("not json"))

    tags = tagging._generate_tags_sync("some quote", api_key="fake-key")

    assert tags == []


def test_generate_tags_sync_handles_wrong_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        tagging, "_client", lambda api_key: _fake_client(json.dumps({"tags": "not-a-list"}))
    )

    tags = tagging._generate_tags_sync("some quote", api_key="fake-key")

    assert tags == []


def test_generate_tags_sync_retries_then_succeeds_on_rate_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(tagging.time, "sleep", lambda _: None)
    attempts = {"count": 0}

    def generate_content(*, model: str, contents: str, config: object) -> _FakeResponse:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise tagging.APIError(429, {"message": "rate limited"})
        return _FakeResponse(json.dumps(["hope"]))

    fake_client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    monkeypatch.setattr(tagging, "_client", lambda api_key: fake_client)

    tags = tagging._generate_tags_sync("some quote", api_key="fake-key")

    assert tags == ["hope"]
    assert attempts["count"] == 2


def test_generate_tags_sync_gives_up_on_non_rate_limit_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def generate_content(*, model: str, contents: str, config: object) -> _FakeResponse:
        raise tagging.APIError(500, {"message": "server error"})

    fake_client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    monkeypatch.setattr(tagging, "_client", lambda api_key: fake_client)

    tags = tagging._generate_tags_sync("some quote", api_key="fake-key")

    assert tags == []


async def test_generate_tags_skips_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tagging, "get_settings", lambda: SimpleNamespace(gemini_api_key=None))

    tags = await tagging.generate_tags("some quote")

    assert tags == []


async def test_create_quote_saves_with_generated_tags(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _fake_generate_tags(text: str) -> list[str]:
        return ["hope", "resolve"]

    monkeypatch.setattr("app.routers.quotes.generate_tags", _fake_generate_tags)

    response = await client.post("/quotes", json={"text": "Some quote"})

    assert response.status_code == 201
    assert response.json()["tags"] == ["hope", "resolve"]


async def test_create_quote_saves_when_tagging_fails(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _failing_generate_tags(text: str) -> list[str]:
        return []

    monkeypatch.setattr("app.routers.quotes.generate_tags", _failing_generate_tags)

    response = await client.post("/quotes", json={"text": "Some quote"})

    assert response.status_code == 201
    assert response.json()["tags"] is None
