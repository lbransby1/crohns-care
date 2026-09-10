import hashlib
import uuid
from typing import Any, Dict, List

import chromadb
import numpy as np
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

from app.schemas import DayHistory


class TokenHashEmbeddingFunction(EmbeddingFunction[Documents]):
    """Stable lexical embeddings so Railway does not need the 80MB ONNX MiniLM download."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def __call__(self, input: Documents) -> Embeddings:
        return [self._embed(text) for text in input]

    def _embed(self, text: str) -> List[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        for tok in str(text).lower().split():
            digest = hashlib.md5(tok.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "little") % self.dim
            vec[idx] += 1.0
        norm = float(np.linalg.norm(vec))
        if norm:
            vec /= norm
        return vec.tolist()

    @staticmethod
    def name() -> str:
        return "token_hash"

    def get_config(self) -> Dict[str, Any]:
        return {"dim": self.dim}

    @staticmethod
    def build_from_config(config: Dict[str, Any]) -> "TokenHashEmbeddingFunction":
        return TokenHashEmbeddingFunction(dim=int(config.get("dim", 256)))

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> None:
        return None


def retrieve_context(history: list[DayHistory]) -> dict[str, str]:
    """Per-request Chroma collection. EphemeralClient is a process singleton, so the
    name must be unique or the second analyze raises Collection already exists."""
    if hasattr(chromadb, "EphemeralClient"):
        client = chromadb.EphemeralClient()
    else:
        client = chromadb.Client()

    name = f"crohns_logs_{uuid.uuid4().hex}"
    collection = client.create_collection(
        name=name,
        embedding_function=TokenHashEmbeddingFunction(),
    )
    try:
        collection.add(
            documents=[day.raw for day in history],
            metadatas=[
                {
                    "day": int(day.day),
                    "date": day.date,
                    "hbi": int(day.hbi),
                    "meds": str(day.meds),
                }
                for day in history
            ],
            ids=[f"day_{day.day}" for day in history],
        )

        queries = {
            "dietary_triggers": "dietary foods eaten spicy curry chicken meals pasta takeaway",
            "complications": "joint pain knee aching mouth ulcers swelling arthralgia fatigue",
            "medication": "medication azathioprine missed skipped dose steroids adherence",
            "stool_pattern": "watery loose liquid stool diarrhea urgency bristol",
        }
        n_results = min(3, len(history))
        return {key: _format_hits(collection, query, n_results) for key, query in queries.items()}
    finally:
        try:
            client.delete_collection(name)
        except Exception:
            pass


def _format_hits(collection, query: str, n_results: int) -> str:
    res = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas"],
    )
    docs = (res.get("documents") or [[]])[0] or []
    metas = (res.get("metadatas") or [[]])[0] or []
    paired = sorted(zip(docs, metas), key=lambda x: int(x[1].get("day", 0)))
    return "\n".join(
        f'- [Day {m["day"]} | HBI: {m["hbi"]} | Meds: {m["meds"]}]: "{d}"' for d, m in paired
    )
