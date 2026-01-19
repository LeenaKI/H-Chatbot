from langgraph.graph import StateGraph, END

from graph.state import GraphState

from graph.nodes.cache_node import semantic_cache_node
from graph.nodes.embed_query_node import embed_query_node
from graph.nodes.vector_search_node import vector_search_node
from graph.nodes.llm_answer_node import llm_answer_node
from graph.nodes.quiz_node import quiz_node

import re

def route_after_cache(state: GraphState):
    # Force fresh generation for Quizzes (Dynamic Content)
    query = state["query"].lower()
    if any(k in query for k in ["quiz", "test", "knowledge"]):
        print("Quiz detected! Skipping Cache to generate fresh questions.")
        return "embed_query"

    if state["cache_hit"]:
        return "end"
    
    # Greeting Bypass Logic
    query = state["query"].lower().strip()
    # Matches common greetings to skip RAG latency
    # Includes: hi, hello, hey, greetings, good morning/afternoon/evening, howdy, how are you, what's up, yo, namaste, hola, sup
    greeting_pattern = r"^(hi|hello|hey|greetings|good\s*(morning|afternoon|evening)|howdy|how\s+are\s+you|what'?s\s*up|yo|namaste|hola|sup|nice\s+to\s+meet\s+you).*"
    
    if re.match(greeting_pattern, query):
        print(" Greeting detected! Skipping Vector Search.")
        return "llm_answer"
        
    return "embed_query"

def route_after_search(state: GraphState):
    query = state["query"].lower()
    
    # Explicitly handle "test drive" to avoid triggering quiz on "test" keyword
    if "test drive" in query:
        return "llm_answer"
        
    if any(k in query for k in ["quiz", "test", "knowledge"]):
        return "quiz_node"
    return "llm_answer"

#build the LangGraph

def build_graph():
    graph = StateGraph(GraphState)

    # Nodes
    graph.add_node("semantic_cache", semantic_cache_node)
    graph.add_node("embed_query", embed_query_node)
    graph.add_node("vector_search", vector_search_node)
    graph.add_node("llm_answer", llm_answer_node)
    graph.add_node("quiz_node", quiz_node)

    # Entry point
    graph.set_entry_point("semantic_cache")

    # Conditional edge from cache
    graph.add_conditional_edges(
        "semantic_cache",
        route_after_cache,
        {
            "embed_query": "embed_query",
            "llm_answer": "llm_answer",
            "end": END
        }
    )

    # Normal RAG flow
    graph.add_edge("embed_query", "vector_search")
    
    # Conditional edge after search (Quiz vs Answer)
    graph.add_conditional_edges(
        "vector_search",
        route_after_search,
        {
            "llm_answer": "llm_answer",
            "quiz_node": "quiz_node"
        }
    )
    
    graph.add_edge("llm_answer", END)
    graph.add_edge("quiz_node", END)

    return graph.compile()
