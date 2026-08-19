import asyncio
import json
import logging
import time
from collections.abc import Callable
from typing import TypeVar

from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.config import get_settings

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-3.5-flash-lite"
MAX_ATTEMPTS = 3
BASE_DELAY_SECONDS = 1.0

_TAG_PROMPT = """Read the following quote and return 3 to 5 short mood/theme tags \
that capture how it feels and what it is about. Use lowercase single words or \
short phrases.

Start from what this specific quote is actually about — do not just pick \
generic or already-popular tags. Then, for each tag you land on, check the \
existing tags below: if one of them names the exact same specific feeling \
or theme (a true synonym, not just a related or broader category), reuse \
that exact existing tag instead of adding a near-duplicate. Otherwise keep \
your own tag. Precision for this quote always wins over reusing an existing \
tag — most quotes will still need at least one tag that isn't in this list.

Existing tags: {existing_tags}

Quote: {text}"""

_EXPLANATION_PROMPT = """A person described how they're feeling: {feeling}

This quote was matched to that feeling:
"{quote}"

In one sentence, explain why this quote resonates with that feeling."""


def _client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


T = TypeVar("T")


def _with_retry(operation: Callable[[], T], *, context: str) -> T | None:
    delay = BASE_DELAY_SECONDS
    last_error: Exception | None = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            return operation()
        except APIError as exc:
            last_error = exc
            if exc.code != 429 or attempt == MAX_ATTEMPTS - 1:
                break
            time.sleep(delay)
            delay *= 2
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            last_error = exc
            break

    logger.warning("%s failed: %s", context, last_error)
    return None


def _generate_tags_sync(
    text: str, api_key: str, existing_tags: list[str] | None = None
) -> list[str]:
    client = _client(api_key)
    existing_display = ", ".join(sorted(existing_tags)) if existing_tags else "(none yet)"

    def _call() -> list[str]:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=_TAG_PROMPT.format(text=text, existing_tags=existing_display),
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

    return _with_retry(_call, context="auto-tagging") or []


def _generate_explanation_sync(feeling: str, quote_text: str, api_key: str) -> str | None:
    client = _client(api_key)

    def _call() -> str:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=_EXPLANATION_PROMPT.format(feeling=feeling, quote=quote_text),
        )
        explanation = (response.text or "").strip()
        if not explanation:
            raise ValueError("model returned an empty explanation")
        return explanation

    return _with_retry(_call, context="mood explanation")


async def generate_tags(text: str, existing_tags: list[str] | None = None) -> list[str]:
    settings = get_settings()
    if not settings.gemini_api_key:
        return []
    return await asyncio.to_thread(
        _generate_tags_sync, text, settings.gemini_api_key, existing_tags
    )


async def generate_explanation(feeling: str, quote_text: str) -> str | None:
    settings = get_settings()
    if not settings.gemini_api_key:
        return None
    return await asyncio.to_thread(
        _generate_explanation_sync, feeling, quote_text, settings.gemini_api_key
    )


def fallback_explanation(feeling: str, tags: list[str] | None) -> str | None:
    """A free, non-LLM explanation for when generate_explanation fails or is
    skipped (quota exhausted, no API key) — built from tags already stored
    on the quote, so it costs no API call.
    """
    if not tags:
        return None
    highlighted = " and ".join(tags[:2])
    return f"This one touches on {highlighted} — themes that often sit close to feeling {feeling}."
