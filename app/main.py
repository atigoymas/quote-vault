from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import quotes, search

app = FastAPI(title="Quote Vault")

# Single-user app, no cookies/auth on requests — open CORS is fine here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quotes.router)
app.include_router(search.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
