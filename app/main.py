from fastapi import FastAPI

from app.routers import quotes, search

app = FastAPI(title="Quote Vault")

app.include_router(quotes.router)
app.include_router(search.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
