import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = os.getenv("GEMINI_MODEL")

from google.genai import errors

def generate_answer(system_prompt, user_prompt, tools=None):
    start = time.time()
    
    max_retries = 5
    base_delay = 2

    for attempt in range(max_retries):
        try:
            #Pass 'tools' to the config
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=tools,
                    temperature=0.7
                )
            )
            break
        except errors.ServerError:
            if attempt < max_retries - 1:
                time.sleep(base_delay * (2 ** attempt))  # Exponential backoff
                continue
            raise
        except errors.ClientError as e:
            if e.code == 429 and attempt < max_retries - 1:
                print(f"⚠️ Quota exceeded. Retrying in {base_delay * (2 ** attempt)}s...")
                time.sleep(base_delay * (2 ** attempt))
                continue
            raise

    elapsed_ms = round((time.time() - start) * 1000, 2)

    input_tokens = response.usage_metadata.prompt_token_count
    output_tokens = response.usage_metadata.candidates_token_count
    
    cached_tokens = getattr(response.usage_metadata, "cached_content_token_count", 0)
    if cached_tokens is None:
        cached_tokens = 0
        
    thoughts_tokens = getattr(response.usage_metadata, "thoughts_token_count", 0)
    if thoughts_tokens is None:
        thoughts_tokens = 0

    # Pricing for Gemini 2.5 Flash (USD per 1M tokens)
    # Verified from screenshot
    INPUT_PRICE_PER_1M = 0.30
    OUTPUT_PRICE_PER_1M = 2.50
    CACHED_PRICE_PER_1M = 0.03
    
    cost_usd = (input_tokens / 1_000_000 * INPUT_PRICE_PER_1M) + \
               ((output_tokens + thoughts_tokens) / 1_000_000 * OUTPUT_PRICE_PER_1M) + \
               (cached_tokens / 1_000_000 * CACHED_PRICE_PER_1M)
               
    cost_inr = cost_usd * 90.26 # Updated conversion rate

    usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cached_tokens": cached_tokens,
        "thoughts_tokens": thoughts_tokens,
        "total_tokens": response.usage_metadata.total_token_count,
        "cost_usd": cost_usd,
        "cost_inr": cost_inr
    }

    return response.text.strip(), usage, elapsed_ms
