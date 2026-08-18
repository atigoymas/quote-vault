from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.database import engine
from app.main import app


@pytest.fixture(autouse=True)
async def _clean_quotes_table() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE quotes RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def _stub_auto_tagging(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _no_tags(text: str) -> list[str]:
        return []

    monkeypatch.setattr("app.routers.quotes.generate_tags", _no_tags)


@pytest.fixture(autouse=True)
def _stub_mood_explanation(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _no_explanation(feeling: str, quote_text: str) -> str | None:
        return None

    monkeypatch.setattr("app.routers.search.generate_explanation", _no_explanation)
