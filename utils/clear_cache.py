import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
CACHE_COLLECTION = os.getenv("SEMANTIC_CACHE_COLLECTION", "Hyundai-semantic-cache")

def clear_cache():
    print(f"🧹 Clearing Semantic Cache Collection: {CACHE_COLLECTION}...")
    
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    if client.collection_exists(CACHE_COLLECTION):
        client.delete_collection(CACHE_COLLECTION)
        print("✅ Cache collection deleted.")
    else:
        print("⚠️ Cache collection not found.")

if __name__ == "__main__":
    clear_cache()
