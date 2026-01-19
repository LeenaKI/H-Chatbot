def calculate_cost(input_tokens, output_tokens, cached_tokens=0, thoughts_tokens=0):
    # Rates defined in gemini_client.py (Verified from screenshot)
    INPUT_PRICE_PER_1M = 0.30
    OUTPUT_PRICE_PER_1M = 2.50
    CACHED_PRICE_PER_1M = 0.03

    cost_input = (input_tokens / 1_000_000) * INPUT_PRICE_PER_1M
    cost_output = ((output_tokens + thoughts_tokens) / 1_000_000) * OUTPUT_PRICE_PER_1M
    cost_cached = (cached_tokens / 1_000_000) * CACHED_PRICE_PER_1M
    
    # Current implementation in gemini_client.py
    current_impl_cost = cost_input + cost_output + cost_cached
    
    print(f"--- Pricing Calculation (Gemini 2.5 Flash Rates) ---")
    print(f"Input Rate: ${INPUT_PRICE_PER_1M}/1M tokens")
    print(f"Output Rate: ${OUTPUT_PRICE_PER_1M}/1M tokens")
    print(f"Cached Rate: ${CACHED_PRICE_PER_1M}/1M tokens")
    print(f"------------------------------------------------")
    print(f"Input Tokens:    {input_tokens:<10} -> ${cost_input:.8f}")
    print(f"Output Tokens:   {output_tokens:<10} -> ${cost_output:.8f}")
    print(f"Cached Tokens:   {cached_tokens:<10} -> ${cost_cached:.8f}")
    print(f"------------------------------------------------")
    print(f"Total Cost (USD): ${current_impl_cost:.8f}")
    print(f"Total Cost (INR): ₹{current_impl_cost * 90:.4f}")
    print(f"------------------------------------------------")
    
    # Analysis of other tokens
    print(f"\n[Note on Special Tokens]")
    print(f"Cached Tokens ({cached_tokens}): Currently $0 in logic. (Industry std: ~${CACHED_PRICE_PER_1M}/1M)")
    print(f"Thoughts Tokens ({thoughts_tokens}): Typically billed as Output. If included in Output count, they are paid. If separate, they need adding.")

if __name__ == "__main__":
    try:
        print("Enter token counts to calculate cost:")
        in_tok = int(input("Input Tokens: ").strip() or 0)
        out_tok = int(input("Output Tokens: ").strip() or 0)
        cached_tok = int(input("Cached Tokens (optional, default 0): ").strip() or 0)
        thoughts_tok = int(input("Thoughts Tokens (optional, default 0): ").strip() or 0)
        
        calculate_cost(in_tok, out_tok, cached_tok, thoughts_tok)
    except ValueError:
        print("Invalid input. Please enter integer values.")
