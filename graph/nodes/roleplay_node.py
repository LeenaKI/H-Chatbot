import json
import os
from llm.gemini_client import generate_answer

def load_scenarios():
    path = os.path.join(os.getcwd(), "data", "roleplay_scenarios.json")
    with open(path, "r") as f:
        return json.load(f)

def roleplay_node(state):
    query = state["query"]
    history = state.get("roleplay_history", [])
    scenario = state.get("roleplay_scenario")
    
    # 1. Handle Exit
    if query.lower() in ["exit", "quit", "end roleplay", "stop"]:
        # The graph router will see this intent and route to evaluation
        # But here we just acknowledge or pass through? 
        # Actually, the router should catch this BEFORE calling this node if we want to skip generation.
        # But if we are here, we might want to say "Ending roleplay..."
        return state

    # 2. Scenario Selection Phase
    if not scenario:
        scenarios = load_scenarios()
        
        # Check if user selected a scenario by ID or Index
        selected = None
        for s in scenarios:
            if s["id"] in query or s["title"].lower() in query.lower():
                selected = s
                break
        
        # Simple numeric selection fallback
        if not selected and query.isdigit():
            idx = int(query) - 1
            if 0 <= idx < len(scenarios):
                selected = scenarios[idx]

        if selected:
            state["roleplay_scenario"] = selected
            # Generate opening line from Persona
            system_prompt = f"""
            You are a roleplay actor. 
            Persona: {selected['persona']}
            
            Your goal is to act out this persona realistically to test the user's sales skills.
            Start the conversation now as this character.
            """
            answer, usage, _ = generate_answer(system_prompt, "Start the conversation.")
            
            state["roleplay_history"] = [
                {"role": "assistant", "content": answer}
            ]
            state["final_answer"] = f"**Scenario Started: {selected['title']}**\n\n{answer}"
            return state
        
        else:
            # List Scenarios
            msg = "Please select a training scenario:\n"
            for i, s in enumerate(scenarios, 1):
                msg += f"{i}. {s['title']} ({s['difficulty']})\n"
            
            state["final_answer"] = msg
            return state

    # 3. Active Roleplay Phase
    system_prompt = f"""
    You are a roleplay actor.
    Persona: {scenario['persona']}
    
    Current Context: You are talking to a Hyundai Sales Consultant (the user).
    
    Rules:
    1. Stay in character 100%. Do not break the fourth wall.
    2. Be challenging but fair. If the user answers well, acknowledge it (in character).
    3. If the user is rude or wrong, react as the customer would.
    4. Keep responses concise (1-2 sentences) to keep the flow moving.
    """
    
    # Format history for LLM
    history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in history])
    user_prompt = f"{history_text}\nUser: {query}\nYou:"
    
    answer, usage, _ = generate_answer(system_prompt, user_prompt)
    
    # Update History
    new_history = history + [
        {"role": "user", "content": query},
        {"role": "assistant", "content": answer}
    ]
    state["roleplay_history"] = new_history
    state["final_answer"] = answer
    
    return state
