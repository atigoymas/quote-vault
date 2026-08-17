from fastapi import FastAPI

from app.routers import quotes

app = FastAPI(title="Quote Vault")

app.include_router(quotes.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
