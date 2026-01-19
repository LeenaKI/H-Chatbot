import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp") 

def inspect():
    print(f"Testing model: {MODEL_NAME}")
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents="Hello",
            config=types.GenerateContentConfig(temperature=0.7)
        )
        
        meta = response.usage_metadata
        print("\n--- Raw Metadata Attributes ---")
        for attr in dir(meta):
            if not attr.startswith("_"):
                val = getattr(meta, attr)
                print(f"{attr}: {val}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
