import sys
import os
import time

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.gemini_client import generate_answer
from utils.quiz_store import add_quiz_to_bank
from graph.nodes.quiz_node import extract_json, QUIZ_SYSTEM_PROMPT

# List of models to generate quizzes for
MODELS = ["Venue", "Creta", "Exter", "GRAND_i10_NIOS", "i20_N_Line", "Venue_n_line", "Alcazar", "Verna", "Kia Sonet", "i20", "Aura", "creta_n_line", "creata_electric"]

from ingestion.qdrant_client import get_qdrant_client
from ingestion.embedder import Embedder
from utils.prompt_formatter import format_context
import os
import glob
import os

# Initialize RAG components (Removed Qdrant)
DATA_DIR = "data"

def get_file_content(model_name):
    """Finds and reads the text file for a specific model."""
    # Simple matching: Look for file containing the model name
    # e.g. "Venue" -> matches "Hyundai_VENUE.txt"
    files = glob.glob(os.path.join(DATA_DIR, "*.txt"))
    
    for f_path in files:
        filename = os.path.basename(f_path).lower()
        if model_name.lower() in filename:
            print(f"   📄 Found file: {filename}")
            with open(f_path, "r", encoding="utf-8") as f:
                return f.read()
                
    return None

def generate_quizzes_for_model(model_name, num_questions=30):
    print(f"Generating {num_questions} questions for {model_name}...")
    
    # 1. Get Real Context from File
    context = get_file_content(model_name)
    
    if not context:
        print(f"No file found for {model_name} in {DATA_DIR}. Skipping.")
        return

    # Truncate context if too long (Gemini Flash has 1M context, so we are safe, but let's be reasonable)
    # Let's use the first 20,000 characters to ensure we capture the main specs/features
    truncated_context = context[:30000] 

    # 2. Generate using Context
    user_prompt = f"""
    Context:
    {truncated_context}
    
    Task:
    Generate {num_questions} Multiple Choice Questions (MCQs) about the Hyundai {model_name} based STRICTLY on the context above.
    Focus on unique features, specifications, and safety.
    Return strictly JSON format.
    """
    
    try:
        answer, _, _ = generate_answer(QUIZ_SYSTEM_PROMPT, user_prompt)
        parsed_answer = extract_json(answer)
        
        if isinstance(parsed_answer, list):
            add_quiz_to_bank(model_name, parsed_answer)
            print(f"   ✅ Added {len(parsed_answer)} questions to bank for {model_name}.")
        else:
            print(f"   ⚠️ Failed to parse JSON for {model_name}.")
            
    except Exception as e:
        print(f"   ❌ Error generating for {model_name}: {e}")

def main():
    print("Starting Quiz Bank Pre-generation...")
    for model in MODELS:
        generate_quizzes_for_model(model, num_questions=30)
        time.sleep(2) # Avoid rate limits
    print("\n All done! Quiz Bank is ready.")

if __name__ == "__main__":
    main()
