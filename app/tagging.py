import asyncio
import json
import logging
import time

from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.config import get_settings

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-3.5-flash-lite"
MAX_ATTEMPTS = 3
BASE_DELAY_SECONDS = 1.0

_PROMPT = """Read the following quote and return 3 to 5 short mood/theme tags \
that capture how it feels and what it is about. Use lowercase single words or \
short phrases.

Quote: {text}"""


def _client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def _generate_tags_sync(text: str, api_key: str) -> list[str]:
    client = _client(api_key)
    delay = BASE_DELAY_SECONDS
    last_error: Exception | None = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=_PROMPT.format(text=text),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=list[str],
                ),
            )
            tags = json.loads(response.text)
            if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
                raise ValueError(f"expected a list of strings, got {tags!r}")
            cleaned = [t.strip().lower() for t in tags if t.strip()]
            if not cleaned:
                raise ValueError("model returned no usable tags")
            return cleaned[:5]
        except APIError as exc:
            last_error = exc
            if exc.code != 429 or attempt == MAX_ATTEMPTS - 1:
                break
            time.sleep(delay)
            delay *= 2
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            last_error = exc
            break

    logger.warning("auto-tagging failed, saving quote without tags: %s", last_error)
    return []


async def generate_tags(text: str) -> list[str]:
    settings = get_settings()
    if not settings.gemini_api_key:
        return []
    return await asyncio.to_thread(_generate_tags_sync, text, settings.gemini_api_key)
