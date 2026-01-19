from llm.gemini_client import generate_answer
from utils.prompt_formatter import format_context

QUIZ_SYSTEM_PROMPT = """
You are an expert Hyundai Sales Trainer.
Your goal is to test the knowledge of a sales consultant based on the provided vehicle context.

Rules:
1.  **Content**: Generate 3 Multiple Choice Questions (MCQs) based STRICTLY on the provided context.
2.  **Difficulty**: Mix of easy (specs) and medium (features/benefits).
3.  **Format**:
    *   Question 1
    *   A) Option
    *   B) Option
    *   C) Option
    *   D) Option
    *   (Correct Answer: X)
    
    ... (Repeat for 3 questions)

4.  **Tone**: Professional and educational.
5.  **Output Format**: Return a valid JSON array of objects. Do NOT use Markdown formatting.
    Example:
    [
        {
            "question": "Question text here?",
            "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
            "correct_answer": "B",
            "explanation": "Concise explanation of why B is correct (1 sentence)."
        },
        ...
    ]
6.  **No Context**: If context is empty, return {"error": "Insufficient context"}.
"""

import json
import re

def extract_json(text):
    try:
        # Try to find JSON block
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(text)
    except:
        return text # Fallback to raw text

from utils.quiz_store import get_adaptive_quiz, add_quiz_to_bank
import re

def quiz_node(state):
    context = format_context(state["retrieved_chunks"])
    query = state["query"]
    user_id = state.get("session_id", "default_user") # Assuming session_id is user_id for now

    # 1. Extract 'N' questions (Default: 3)
    match = re.search(r'(\d+)\s*questions?', query.lower())
    n_questions = int(match.group(1)) if match else 3
    
    # 2. Identify Model (Simple heuristic or use existing metadata)
    # For now, we try to find the model name in the query or context
    # This is a simplification. Ideally, 'vector_search' should pass the detected model.
    # Let's assume we can get it from the first retrieved chunk's metadata if available, 
    # or fallback to a default if we can't reliably detect it here without the 'model' metadata passed explicitly.
    # A better way: The 'vector_search_node' already detects models. We should pass that in 'state'.
    # For this iteration, let's try to extract from query again or use a placeholder.
    # actually, let's look at the retrieved chunks.
    model_name = "General"
    if state["retrieved_chunks"]:
        # Try to get model from the first chunk's source filename or metadata
        # But 'retrieved_chunks' is a list of dicts with 'source'.
        # Let's just use the query for now as a key.
        # WAIT: The user wants "Quiz me on Venue". 'Venue' is the key.
        # We need to extract the model name reliably.
        # Let's re-use the KNOWN_MODELS logic or just rely on the LLM to generate valid questions if we miss.
        # To make the BANK work, we need a consistent key.
        # Let's try to find a known model in the query.
        pass

    # IMPROVEMENT: We need to know WHICH model to fetch from the bank.
    # Let's do a quick check against KNOWN_MODELS (imported or redefined)
    # Since we can't easily import KNOWN_MODELS without circular deps or refactoring, 
    # let's assume the LLM generation path handles the "first time" and we infer the key then?
    # No, we need the key to fetch.
    
    # Let's define a simple helper here or import if possible.
    # For now, let's just use the first word that looks like a model or "General".
    
    # ... (skipping complex model detection for this step to keep it simple) ...
    # Let's assume the user query contains the model name.
    
    # 3. Try to get from Bank
    # We need a valid model key. Let's try to extract it from the query using a simple list.
    target_model = "General"
    keywords = ["venue", "creta", "exter", "alcazar", "verna", "aura", "i20", "grand i10", "nios", "ioniq", "sonet", "seltos"]
    for k in keywords:
        if k in query.lower():
            target_model = k.title() # e.g. "Venue"
            break
            
    cached_quiz = get_adaptive_quiz(user_id, target_model, n_questions)
    
    if cached_quiz:
        print(f"🎓 Serving Adaptive Quiz from Bank for {target_model} (Count: {len(cached_quiz)})")
        state["final_answer"] = cached_quiz
        return state

    # 4. If not in bank (or not enough), Generate via LLM
    user_prompt = f"""
                    Context:
                    {context}

                    User Request:
                    {query}

                    Generate {n_questions} MCQs in JSON format now.
                    """

    answer, usage, latency_ms = generate_answer(
        QUIZ_SYSTEM_PROMPT,
        user_prompt
    )
    
    # Parse JSON answer
    parsed_answer = extract_json(answer)
    
    # 5. Save to Bank
    if isinstance(parsed_answer, list):
        add_quiz_to_bank(target_model, parsed_answer)

    # Update conversation history
    state["conversation_history"].extend([
        {"role": "user", "content": query},
        {"role": "assistant", "content": str(parsed_answer)}
    ])

    state["final_answer"] = parsed_answer
    state["metrics"]["llm_time_ms"] = latency_ms
    state["metrics"].update(usage)

    return state
