from collections.abc import AsyncGenerator
from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app import rate_limit
from app.database import engine
from app.main import app

TEST_OWNER_KEY = "test-owner-key"


@pytest.fixture(autouse=True)
async def _clean_quotes_table() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE quotes RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture(autouse=True)
def _reset_rate_limits() -> None:
    rate_limit.reset()


@pytest.fixture(autouse=True)
def _configure_owner_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.rate_limit.get_settings", lambda: SimpleNamespace(owner_access_key=TEST_OWNER_KEY)
    )


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-Owner-Key": TEST_OWNER_KEY},
    ) as ac:
        yield ac


@pytest.fixture(autouse=True)
def _stub_auto_tagging(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _no_tags(text: str, existing_tags: list[str] | None = None) -> list[str]:
        return []

    monkeypatch.setattr("app.routers.quotes.generate_tags", _no_tags)


@pytest.fixture(autouse=True)
def _stub_mood_explanation(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _no_explanation(feeling: str, quote_text: str) -> str | None:
        return None

    monkeypatch.setattr("app.routers.search.generate_explanation", _no_explanation)
