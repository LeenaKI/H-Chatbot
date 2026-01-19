"""
Full document
   ↓
split_by_sections()
   ↓
(section_title, section_text)
   ↓
chunk_text(section_text)
   ↓
chunks WITH category metadata
"""

import uuid
import os
from ingestion.loader import load_txt
from ingestion.chunker import clean_text, split_by_sections, chunk_text
from ingestion.embedder import Embedder
from ingestion.qdrant_client import get_qdrant_client
from ingestion.config import COLLECTION_NAME
from qdrant_client.models import PointStruct, VectorParams, Distance
from utils.metrics import IngestionMetrics

def ingest_txt_to_qdrant(txt_path: str, model_name: str, vehicle_type: str):

    metrics = IngestionMetrics(txt_path)
    metrics.start()

    raw_text = load_txt(txt_path)
    cleaned_text = clean_text(raw_text)

    sections = split_by_sections(cleaned_text)

    embedder = Embedder()
    client = get_qdrant_client()

    # NOTE: Collection creation is handled by run_ingest.py

    points = []

    for section_title, section_text in sections:
        section_chunks = chunk_text(section_text, max_tokens=350)

        for chunk in section_chunks:
            vector = embedder.embed(chunk)

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "model": model_name,         # ✅ DYNAMIC
                    "vehicle_type": vehicle_type, # ✅ DYNAMIC
                    "category": section_title,
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

