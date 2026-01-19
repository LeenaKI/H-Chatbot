from llm.gemini_client import generate_answer

def evaluation_node(state):
    history = state.get("roleplay_history", [])
    scenario = state.get("roleplay_scenario")
    
    if not history or not scenario:
        state["final_answer"] = "No roleplay history found to evaluate."
        return state

    system_prompt = """
    You are an Expert Sales Coach.
    Your task is to evaluate a transcript between a Sales Consultant (User) and a Customer (AI).
    
    Analyze the Sales Consultant's performance based on:
    1. **Empathy**: Did they listen to the customer's needs?
    2. **Product Knowledge**: Did they use correct information?
    3. **Objection Handling**: How well did they manage concerns?
    4. **Closing**: Did they try to move the deal forward?
    
    Output Format:
    **Score**: X/10
    
    **Strengths**:
    - ...
    
    **Areas for Improvement**:
    - ...
    
    **Overall Feedback**:
    ...
    """
    
    transcript = f"Scenario: {scenario['title']}\nPersona: {scenario['persona']}\n\nTranscript:\n"
    for msg in history:
        transcript += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
    answer, usage, _ = generate_answer(system_prompt, transcript)
    
    # Reset Roleplay State after evaluation
    state["roleplay_active"] = False
    state["roleplay_scenario"] = None
    state["roleplay_history"] = []
    
    state["final_answer"] = answer
    state["evaluation_result"] = {"feedback": answer}
    
    return state
