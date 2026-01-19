import time
import os
import re
from dotenv import load_dotenv
from ingestion.qdrant_client import get_qdrant_client
from qdrant_client import models

load_dotenv()

KNOWLEDGE_COLLECTION = os.getenv("COLLECTION_NAME")
TOP_K = int(os.getenv("TOP_K", 5))

# Mapping of User Keywords -> Qdrant 'model' payload values
# Note: These values depend on how run_ingest.py parses filenames.
KNOWN_MODELS = {
    # SUV
    "venue": ["VENUE", "VENUE N Line"],
    "creta": ["Creta", "CRETA", "CRETA N Line", "CRETA Electric"],
    "exter": ["EXTER"],
    "alcazar": ["Alcazar"],
    
    # Sedan
    "verna": ["Verna"],
    "aura": ["AURA"],
    
    # Hatchback
    "i20": ["i20", "i20 N Line"],
    "grand i10": ["GRAND i10 NIOS"],
    "nios": ["GRAND i10 NIOS"],
    
    # Electric
    "ioniq": ["IONIQ 5"],
    
    # Competitors
    "sonet": ["Kia Sonet"],
    "seltos": ["Kia Seltos"]
}

def vector_search_node(state):
    """
    LangGraph node: Retrieve relevant knowledge chunks
    """
    start = time.time()

    client = get_qdrant_client()
    query_vector = state["query_embedding"]
    query_text = state["query"].lower()

    # 1. Detect Models in Query
    detected_payload_values = []
    for keyword, payload_list in KNOWN_MODELS.items():
        # Use regex to match whole words only (prevents "exterior" matching "exter")
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, query_text):
            detected_payload_values.extend(payload_list)
    
    # 2. Build Filter (if models found)
    query_filter = None
    if detected_payload_values:
        print(f"Detected Models: {detected_payload_values} -> Applying Filter")
        should_conditions = [
            models.FieldCondition(
                key="model",
                match=models.MatchValue(value=val)
            ) for val in detected_payload_values
        ]
        query_filter = models.Filter(should=should_conditions)

    results = client.query_points(
        collection_name=KNOWLEDGE_COLLECTION,
        query=query_vector,
        limit=TOP_K,
        query_filter=query_filter, # Apply Filter
        with_payload=True
    ).points

    retrieved = []

    for hit in results:
        retrieved.append({
            "text": hit.payload.get("text"),
            "source": hit.payload.get("source"),
            "category": hit.payload.get("category"),
            "score": hit.score
        })

    elapsed_ms = round((time.time() - start) * 1000, 2)

    state["retrieved_chunks"] = retrieved
    state["metrics"]["vector_search_time_ms"] = elapsed_ms

    return state
