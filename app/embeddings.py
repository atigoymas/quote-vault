from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastembed import TextEmbedding

# ONNX Runtime instead of sentence-transformers/torch — same model and output
# vectors, a fraction of the memory footprint (matters on constrained hosts).
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Explicit, in-repo cache dir (not the OS temp dir) so a model fetched during
# a host's build step is still there at runtime.
CACHE_DIR = Path(__file__).resolve().parent.parent / ".fastembed_cache"


@lru_cache
def get_model() -> TextEmbedding:
    from fastembed import TextEmbedding

    return TextEmbedding(model_name=MODEL_NAME, cache_dir=str(CACHE_DIR))


def embed_text(text: str) -> list[float]:
    (embedding,) = get_model().embed([text])
    return embedding.tolist()
