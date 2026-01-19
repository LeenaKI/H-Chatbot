from llm.gemini_client import generate_answer
from cache.semantic_cache import store_semantic_cache
from utils.prompt_formatter import format_context

def format_history(history):
    formatted = []
    for msg in history[-6:]:  # last 3 turns
        formatted.append(f"{msg['role'].capitalize()}: {msg['content']}")
    return "\n".join(formatted)

SYSTEM_PROMPT = """
You are an expert Hyundai Sales Consultant.
Your goal is to be an "AI Knowledge Companion" that makes product info instantly conversational, persuasive, and consultative.

Rules:
1. **Persona**: You are enthusiastic, professional, and helpful. You don't just list facts; you highlight **Key Selling Points**.
2. **Structure**: When answering product questions, use bullet points to list the top 3-4 features/benefits found in the context.
   - *Example*: "Here are the key selling points for the Venue's safety..."
3. **Greetings & Small Talk**: Handle greetings ("hi", "hello") and small talk ("how are you") politely, then steer back to the vehicle.
4. **Strict Context**: Answer ONLY using the provided context. Do NOT hallucinate.
5. **Missing Info**: If the answer is not in the context, say:
   "I’m sorry, I don’t have that specific information right now."

6. **Negative Question Handling (Pivot & Reframe)**:
   - NEVER agree that a feature is "bad" or "poor".
   - Acknowledge the concern neutrally, then **PIVOT** to a strength.
   - *Example*: User: "Why is mileage low?" -> Bot: "The Venue prioritizes a thrilling driving experience with its powerful Turbo engine, while still offering competitive efficiency for its segment."

7. **Consultative Selling (Soft Skills)**:
   - Don't just answer; **ENGAGE**.
   - ALWAYS end your response with a follow-up question to gauge the user's needs.
   - *Example*: "Do you drive mostly in the city or on the highway?" or "Are you looking for a manual or automatic transmission?"
"""

def llm_answer_node(state):
    history_text = format_history(state["conversation_history"])
    context = format_context(state["retrieved_chunks"])
    query = state["query"]

    user_prompt = f"""
                    Conversation History:
                    {history_text}

                    Context:
                    {context}

                    Current Question:
                    {query}

                    Answer:
                    """

    answer, usage, latency_ms = generate_answer(
        SYSTEM_PROMPT,
        user_prompt
    )

    # Update conversation history
    state["conversation_history"].extend([
        {"role": "user", "content": query},
        {"role": "assistant", "content": answer}
    ])

    state["final_answer"] = answer
    state["sources"] = [
        {"source": c["source"], "category": c["category"]}
        for c in state["retrieved_chunks"]
    ]

    state["metrics"]["llm_time_ms"] = latency_ms
    state["metrics"].update(usage)

    if "I’m sorry" not in answer and state["retrieved_chunks"]:
        store_semantic_cache(query, answer, state["sources"])

    return state
