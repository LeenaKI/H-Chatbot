import os
import time
from qdrant_client.models import VectorParams, Distance, PointStruct
from ingestion.qdrant_client import get_qdrant_client
from ingestion.embedder import Embedder
from dotenv import load_dotenv
import uuid

load_dotenv()

CACHE_COLLECTION = os.getenv("SEMANTIC_CACHE_COLLECTION")
CACHE_THRESHOLD = float(os.getenv("SEMANTIC_CACHE_THRESHOLD", 0.82))

embedder = Embedder()


def ensure_cache_collection():
    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]

    if CACHE_COLLECTION not in collections:
        client.create_collection(
            collection_name=CACHE_COLLECTION,
            vectors_config=VectorParams(
                size=1024,
                distance=Distance.COSINE
            )
        )


def search_semantic_cache(query: str):
    """
    Returns cached result if similarity >= threshold
    """
    client = get_qdrant_client()
    query_vector = embedder.embed(query)

    results = client.query_points(
        collection_name=CACHE_COLLECTION,
        query=query_vector,
        limit=1
    ).points

    if not results:
        return None

    top_hit = results[0]

    if top_hit.score >= CACHE_THRESHOLD:
        return {
            "answer": top_hit.payload["answer"],
            "sources": top_hit.payload["sources"],
            "score": top_hit.score
        }

    return None


def store_semantic_cache(query, answer, sources):
    """
    Stores a new semantic cache entry
    """
    client = get_qdrant_client()
    vector = embedder.embed(query)

    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload={
            "query": query,
            "answer": answer,
            "sources": sources,
            "model": "Hyundai Venue",
            "created_at": time.time()
        }
    )

    client.upsert(
        collection_name=CACHE_COLLECTION,
        points=[point]
    )
