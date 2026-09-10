import chromadb
from chromadb.utils import embedding_functions

from app.schemas import DayHistory

_emb_fn = None


def _embedding_fn():
    global _emb_fn
    if _emb_fn is None:
        _emb_fn = embedding_functions.DefaultEmbeddingFunction()
    return _emb_fn


def _chroma_client():
    if hasattr(chromadb, "EphemeralClient"):
        return chromadb.EphemeralClient()
    return chromadb.Client()


def retrieve_context(history: list[DayHistory]) -> dict[str, str]:
    """Ephemeral per-request Chroma index so patients never share embeddings."""
    client = _chroma_client()
    collection = client.create_collection(
        name="crohns_logs",
        embedding_function=_embedding_fn(),
    )
    collection.add(
        documents=[day.raw for day in history],
        metadatas=[
            {"day": day.day, "date": day.date, "hbi": day.hbi, "meds": str(day.meds)}
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
    return {name: _format_hits(collection, query, n_results) for name, query in queries.items()}


def _format_hits(collection, query: str, n_results: int) -> str:
    res = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas"],
    )
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    paired = sorted(zip(docs, metas), key=lambda x: x[1]["day"])
    return "\n".join(
        f'- [Day {m["day"]} | HBI: {m["hbi"]} | Meds: {m["meds"]}]: "{d}"' for d, m in paired
    )
