import os
import glob
from ingestion.ingest_pipeline import ingest_txt_to_qdrant
from ingestion.qdrant_client import get_qdrant_client
from ingestion.config import COLLECTION_NAME
from qdrant_client.models import VectorParams, Distance
from qdrant_client import models

DATA_DIR = "data"

def main():
    print(f"🚀 Starting Ingestion for Collection: {COLLECTION_NAME}...")
    client = get_qdrant_client()
    
    # 1. Ensure Collection Exists (Create if not exists)
    if not client.collection_exists(collection_name=COLLECTION_NAME):
        print(f"🆕 Collection not found. Creating {COLLECTION_NAME}...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )
    else:
        print(f"✅ Collection {COLLECTION_NAME} already exists.")

    # Ensure index on 'source' field for fast filtering
    print("⚙️  Ensuring index on 'source' field...")
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="source",
        field_schema=models.PayloadSchemaType.KEYWORD
    )

    # Ensure index on 'model' field for metadata filtering
    print("⚙️  Ensuring index on 'model' field...")
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="model",
        field_schema=models.PayloadSchemaType.KEYWORD
    )

    # 2. Find all .txt files
    txt_files = glob.glob(os.path.join(DATA_DIR, "*.txt"))
    
    if not txt_files:
        print("⚠️ No .txt files found in data/ directory!")
        return

    print(f"📂 Found {len(txt_files)} files in data directory.")

    # Define Vehicle Types based on User Images
    MODEL_TYPES = {
        # SUV
        "Venue": "SUV",
        "Venue N Line": "SUV",
        "Creta": "SUV",
        "Creta N Line": "SUV",
        "Exter": "SUV",
        "Alcazar": "SUV",
        
        # Sedan
        "Verna": "Sedan",
        "Aura": "Sedan",
        
        # Hatchback
        "i20": "Hatchback",
        "i20 N Line": "Hatchback",
        "Grand i10 Nios": "Hatchback",
        
        # Electric
        "Ioniq 5": "Electric",
        "Creta Electric": "Electric"
    }

    # List of Competitor Brands for auto-detection
    COMPETITOR_BRANDS = ["Kia", "Maruti", "Toyota", "Tata", "Mahindra", "Honda", "MG", "Skoda", "Volkswagen"]

    import sys
    force_update = "--force" in sys.argv

    # 3. Ingest each file (INCREMENTAL CHECK)
    for txt_path in txt_files:
        filename = os.path.basename(txt_path)
        
        # Check if file is already ingested
        # We query for 1 point with this source to see if it exists
        if not force_update:
            existing_points = client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="source",
                            match=models.MatchValue(value=filename)
                        )
                    ]
                ),
                limit=1
            )[0]

            if existing_points:
                print(f"⏭️  Skipping {filename} (Already ingested)")
                continue
        else:
            print(f"🔄 Force updating {filename}...")
        
        # Extract Model Name (e.g., "Hyundai_VENUE_N_Line.txt" -> "VENUE N Line")
        if filename.lower().startswith("hyundai_"):
            # Remove "Hyundai_" prefix (8 chars) and extension
            raw_name = filename[8:].rsplit(".", 1)[0]
            model_name = raw_name.replace("_", " ")
        else:
            model_name = filename.rsplit(".", 1)[0].replace("_", " ")
            
        # Determine Vehicle Type
        vehicle_type = "Unknown"
        
        # 1. Check specific Hyundai models
        for key, v_type in MODEL_TYPES.items():
            if key.lower() in model_name.lower().replace("_", " "):
                vehicle_type = v_type
                break
        
        # 2. If not found, check if it's a Competitor Brand
        if vehicle_type == "Unknown":
            for brand in COMPETITOR_BRANDS:
                if brand.lower() in filename.lower():
                    vehicle_type = "Competitor"
                    break
            
        print(f"\n📥 Ingesting: {filename} (Model: {model_name}, Type: {vehicle_type})")
        ingest_txt_to_qdrant(txt_path, model_name, vehicle_type)

    print("\n✅ Ingestion process complete!")

if __name__ == "__main__":
    main()
