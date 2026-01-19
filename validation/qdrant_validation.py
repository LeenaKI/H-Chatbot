#run  this file to validate that ingestion was successful and vectors can be queried
#python -m validation.qdrant_validation

from ingestion.embedder import Embedder
from ingestion.qdrant_client import get_qdrant_client
from ingestion.config import COLLECTION_NAME

def validate_query(query: str, top_k: int = 5):
    embedder = Embedder()
    client = get_qdrant_client()

    query_vector = embedder.embed(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    ).points


    print("\n🔍 QUERY:", query)
    print("-" * 50)

    for i, hit in enumerate(results, start=1):
        print(f"\nResult {i}")
        print("Score:", round(hit.score, 4))
        print("Source:", hit.payload.get("source"))
        print("Category:", hit.payload.get("category"))
        print("Text Snippet:")
        print(hit.payload.get("text")[:300], "...")

if __name__ == "__main__":
    validate_query("Does Hyundai Venue have 6 airbags?")
    validate_query("What are the safety features of Hyundai Venue?")

