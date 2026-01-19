from typing import TypedDict, List, Dict, Any

class Message(TypedDict):
    role: str   # "user" | "assistant"
    content: str

class GraphState(TypedDict):
    query: str
    cache_hit: bool

    conversation_history: List[Message]

    query_embedding: List[float]
    retrieved_chunks: List[Dict[str, Any]]

    final_answer: str
    sources: List[Dict[str, str]]

    metrics: Dict[str, Any]
