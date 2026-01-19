import time
from cache.semantic_cache import (
    ensure_cache_collection,
    search_semantic_cache
)

def semantic_cache_node(state):
    """
    LangGraph Semantic Cache Node
    """
    ensure_cache_collection()

    start = time.time()
    query = state["query"]

    cached = search_semantic_cache(query)

    elapsed_ms = round((time.time() - start) * 1000, 2)
    state["metrics"]["cache_time_ms"] = elapsed_ms

    if cached:
        state["cache_hit"] = True
        state["final_answer"] = cached["answer"]
        state["sources"] = cached["sources"]
        state["metrics"]["semantic_cache_score"] = cached["score"]
    else:
        state["cache_hit"] = False
    
    state["metrics"]["cache_hit"] = state["cache_hit"]

    return state
