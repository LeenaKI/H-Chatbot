import time
from ingestion.embedder import Embedder

embedder = Embedder()

def embed_query_node(state):
    """
    LangGraph node: Embed user query
    """
    start = time.time()

    query = state["query"]
    embedding = embedder.embed(query)

    elapsed_ms = round((time.time() - start) * 1000, 2)

    state["query_embedding"] = embedding
    state["metrics"]["query_embedding_time_ms"] = elapsed_ms

    return state
