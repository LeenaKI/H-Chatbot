from functools import lru_cache
from qdrant_client import QdrantClient
from ingestion.config import QDRANT_URL, QDRANT_API_KEY

@lru_cache(maxsize=1)
def get_qdrant_client():
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )
