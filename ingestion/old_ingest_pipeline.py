"""
Full document
   ↓
chunk_text(cleaned)
   ↓
chunks (no category context)
"""
import uuid
import os
from ingestion.loader import load_txt
from ingestion.old_chunker import clean_text, chunk_text
from ingestion.embedder import Embedder
from ingestion.qdrant_client import get_qdrant_client
from ingestion.config import COLLECTION_NAME
from qdrant_client.models import PointStruct, VectorParams, Distance
from utils.metrics import IngestionMetrics

def ingest_txt_to_qdrant(txt_path: str):

    metrics = IngestionMetrics(txt_path)
    metrics.start()

    raw_text = load_txt(txt_path)
    cleaned = clean_text(raw_text)

    chunks = chunk_text(cleaned, max_tokens=350)

    embedder = Embedder()
    client = get_qdrant_client()

    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
    )

    points = []
    for chunk in chunks:
        vector = embedder.embed(chunk)

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "model": "Hyundai Venue",
                "category": "general",
                "source": os.path.basename(txt_path),
                "text": chunk
            }
        )
        points.append(point)

    client.upsert(collection_name=COLLECTION_NAME, points=points)

    metrics.stop()

    print("📊 Ingestion Metrics")
    print("------------------")
    print(f"File name      : {os.path.basename(txt_path)}")
    print(f"File size (KB) : {metrics.file_size_kb()} KB")
    print(f"Chunks created : {len(points)}")
    print(f"Time taken    : {metrics.duration_seconds()} seconds")

