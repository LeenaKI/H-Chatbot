from sentence_transformers import SentenceTransformer
from ingestion.config import EMBED_MODEL

class Embedder:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Embedder, cls).__new__(cls)
            # Load model locally (Force CPU to avoid OOM on small GPUs)
            cls._instance.model = SentenceTransformer(EMBED_MODEL, device="cpu")
        return cls._instance

    def embed(self, text: str):
        # Returns a list of floats
        embedding = self.model.encode(text).tolist()
        return embedding

def get_embedder():
    return Embedder()
