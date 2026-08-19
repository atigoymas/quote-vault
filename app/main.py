from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import quotes, search

app = FastAPI(title="Quote Vault")

# Source and this Render service name are public — CORS is scoped to the
# real frontend (not "*") so the Gemini-calling routes aren't trivially
# embeddable elsewhere; enforce_rate_limit backstops direct API abuse.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://quote-vault-rose.vercel.app",
        "http://localhost:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quotes.router)
app.include_router(search.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
