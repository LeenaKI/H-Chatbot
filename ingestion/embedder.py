from sentence_transformers import SentenceTransformer
from ingestion.config import EMBED_MODEL

class Embedder:
    def __init__(self):
        # Load model locally (Force CPU to avoid OOM on small GPUs)
        self.model = SentenceTransformer(EMBED_MODEL, device="cpu")

    def embed(self, text: str):
        # Returns a list of floats
        embedding = self.model.encode(text).tolist()
        return embedding
