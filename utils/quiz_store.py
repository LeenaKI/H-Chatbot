import json
import os
import random
import uuid
from typing import List, Dict, Optional

QUIZ_BANK_FILE = "data/quiz_bank.json"
USER_PROGRESS_FILE = "data/user_progress.json"

def _load_json(filepath: str) -> Dict:
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def _save_json(filepath: str, data: Dict):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def get_adaptive_quiz(user_id: str, model_name: str, n: int = 3) -> Optional[List[Dict]]:
    """
    Selects 'n' questions adaptively:
    1. Prioritize questions answered WRONG previously.
    2. Fill with UNSEEN questions.
    3. Exclude CORRECT (mastered) questions.
    """
    bank = _load_json(QUIZ_BANK_FILE)
    progress = _load_json(USER_PROGRESS_FILE)
    
    if model_name not in bank:
        return None
        
    all_questions = bank[model_name]
    user_history = progress.get(user_id, {})
    
    # Categorize questions
    wrong_questions = []
    unseen_questions = []
    
    for q in all_questions:
        q_id = q.get("id")
        # Assign ID if missing (legacy support)
        if not q_id:
            q_id = str(uuid.uuid4())
            q["id"] = q_id
            
        status = user_history.get(q_id)
        
        if status == "wrong":
            wrong_questions.append(q)
        elif status is None:
            unseen_questions.append(q)
        # If status == "correct", we skip it (Mastered)
            
    selected_questions = []
    
    # 1. Pick Wrong Questions first (Spaced Repetition)
    # Shuffle to avoid same order
    random.shuffle(wrong_questions)
    selected_questions.extend(wrong_questions[:n])
    
    # 2. Fill remaining slots with Unseen
    slots_needed = n - len(selected_questions)
    if slots_needed > 0:
        if len(unseen_questions) >= slots_needed:
            selected_questions.extend(random.sample(unseen_questions, slots_needed))
        else:
            # Not enough unseen, take all of them
            selected_questions.extend(unseen_questions)
            
    # If we still don't have enough (e.g., user mastered everything), 
    # we might need to return None to trigger generation of NEW questions.
    if len(selected_questions) < n:
        return None 
        
    return selected_questions

def add_quiz_to_bank(model_name: str, new_questions: List[Dict]):
    """Adds new questions to the bank."""
    bank = _load_json(QUIZ_BANK_FILE)
    if model_name not in bank:
        bank[model_name] = []
    
    existing_texts = {q["question"] for q in bank[model_name]}
    
    updated = False
    for q in new_questions:
        if q["question"] not in existing_texts:
            # Ensure ID
            if "id" not in q:
                q["id"] = str(uuid.uuid4())
            bank[model_name].append(q)
            updated = True
            
    if updated:
        _save_json(QUIZ_BANK_FILE, bank)

def record_attempt(user_id: str, question_id: str, is_correct: bool):
    """Updates user progress."""
    progress = _load_json(USER_PROGRESS_FILE)
    if user_id not in progress:
        progress[user_id] = {}
        
    progress[user_id][question_id] = "correct" if is_correct else "wrong"
    _save_json(USER_PROGRESS_FILE, progress)

def clear_model_bank(model_name: str):
    """Deletes all quizzes for a specific model."""
    bank = _load_json(QUIZ_BANK_FILE)
    if model_name in bank:
        del bank[model_name]
        _save_json(QUIZ_BANK_FILE, bank)
        print(f"iCleared Quiz Bank for model: {model_name}")
