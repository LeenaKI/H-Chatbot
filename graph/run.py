from graph.graph_builder import build_graph

graph = build_graph()

def run_query(user_query, session_state=None):
    if session_state is None:
        session_state = {
            "conversation_history": []
        }

    initial_state = {
        "query": user_query,
        "cache_hit": False,

        "conversation_history": session_state["conversation_history"],

        "query_embedding": [],
        "retrieved_chunks": [],

        "final_answer": "",
        "sources": [],
        "metrics": {}
    }

    result = graph.invoke(initial_state)
    
    # Calculate Total Latency
    metrics = result.get("metrics", {})
    total_latency = 0
    for k, v in metrics.items():
        if k.endswith("_time_ms"):
            total_latency += v
    metrics["total_latency_ms"] = round(total_latency, 2)
    result["metrics"] = metrics

    return result

