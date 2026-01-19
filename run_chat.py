import time
import sys
from graph.run import run_query

# ANSI Colors for better terminal UI
GREEN = "\033[92m"
CYAN = "\033[96m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_thinking():
    """Simulates a thinking indicator"""
    sys.stdout.write(f"{YELLOW}Thinking...{RESET}")
    sys.stdout.flush()

def clear_line():
    """Clears the current line"""
    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.flush()

def main():
    print(f"{BOLD}{GREEN}Hyundai Sales Buddy {RESET}")
    print(f"{CYAN}Type 'exit' or 'quit' to stop.{RESET}")
    print(f"{CYAN}Type '/clear' to reset conversation history.{RESET}")
    print("-" * 60)

    # Initialize conversation history (handled by the graph state internally, 
    # but we can simulate a session reset by just restarting the loop or clearing state if we had a state manager)
    # Note: run_query currently creates a fresh state each time unless we modify it to accept history.
    # Wait, looking at graph/run.py, it initializes state = {"query": query, "conversation_history": []}
    # So `run_query` as currently written DOES NOT persist history across calls in a simple way 
    # unless we modify `run_query` or pass history in.
    
    # Let's check graph/run.py first to be sure. 
    # If run_query resets history every time, this CLI won't work as intended for multi-turn.
    # I will assume I need to manage history here and pass it, OR modify run_query.
    # Initialize session state
    session_state = {
        "conversation_history": []
    }

    while True:
        try:
            user_input = input(f"\n{BOLD}You:{RESET} ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit']:
                print(f"\n{GREEN}Thanks for using Hyundai Sales Buddy! Feel free to reach out if you have any other questions.{RESET}")
                break
                
            if user_input.lower() == '/clear':
                session_state["conversation_history"] = []
                print(f"{YELLOW} Conversation history cleared.{RESET}")
                continue

            print_thinking()
            
            start_time = time.time()
            
            # Pass session_state to persist history
            response = run_query(user_input, session_state)
            
            # Update session_state with the new history from the result
            session_state["conversation_history"] = response["conversation_history"]
            
            latency_ms = round((time.time() - start_time) * 1000, 2)
            clear_line()
            
            # The original `answer` assignment is replaced/modified here
            sources = response.get('retrieved_chunks', [])
            
            # Display Bot Response
            print(f"{BLUE}Bot:{RESET}", end=" ")
            
            answer = response.get("final_answer", "") # Use "final_answer" key from graph state
            
            if isinstance(answer, list):
                # It's a structured Quiz!
                print("\nHere is your quiz!\n")
                
                from utils.quiz_store import record_attempt
                user_id = "default_user" # In a real app, this comes from login
                
                for i, q in enumerate(answer, 1):
                    print(f"{BOLD}Question {i}{RESET}")
                    print(f"{q.get('question')}")
                    options = q.get('options', [])
                    for opt in options:
                        print(f"  {opt}")
                    
                    # Interactive Answering
                    while True:
                        user_ans = input(f"\n{CYAN}Your Answer (A/B/C/D):{RESET} ").strip().upper()
                        if user_ans in ['A', 'B', 'C', 'D']:
                            break
                        print(f"{RED}Invalid input. Please enter A, B, C, or D.{RESET}")
                    
                    correct_ans = q.get('correct_answer', '').strip().upper()
                    # Handle cases where correct answer might be "Option A" or just "A"
                    # We assume the JSON has just "A", "B", etc. or we extract it.
                    # Simple check:
                    is_correct = user_ans == correct_ans
                    
                    if is_correct:
                        print(f"{GREEN}Correct!{RESET}")
                    else:
                        print(f"{RED}Wrong!{RESET} The correct answer was {BOLD}{correct_ans}{RESET}.")
                    
                    # Show Explanation if available
                    explanation = q.get('explanation')
                    if explanation:
                        print(f"{CYAN}{explanation}{RESET}\n")
                    else:
                        print("\n") # Just a newline if no explanation
                    
                    # Save Progress
                    q_id = q.get("id")
                    if q_id:
                        record_attempt(user_id, q_id, is_correct)
                        
                print(f"{YELLOW}Quiz Complete! Your progress has been saved.{RESET}")

            else:
                # Normal text response
                print(f"{answer}")
            
            # Print Metadata
            print(f"\n{CYAN}[Metadata]{RESET}")
            
            metrics = response.get("metrics", {})
            
            # Cache Status
            if "cache_hit" in metrics:
                status = f"{GREEN} HIT{RESET}" if metrics["cache_hit"] else f"{YELLOW} MISS{RESET}"
                print(f" Cache: {status}")

            print(f"Latency: {latency_ms} ms")
            if "cost_usd" in metrics:
                cost = metrics["cost_usd"]
                cost_inr = metrics.get("cost_inr", 0.0)
                input_tok = metrics.get("input_tokens", 0)
                output_tok = metrics.get("output_tokens", 0)
                cached_tok = metrics.get("cached_tokens", 0)
                thoughts_tok = metrics.get("thoughts_tokens", 0)
                total_tok = metrics.get("total_tokens", 0)
                
                print(f"Cost: ${cost:.6f} (₹{cost_inr:.4f})")
                print(f"Tokens: {total_tok} (In: {input_tok}, Out: {output_tok}, Cached: {cached_tok}, Thoughts: {thoughts_tok})")
            
            if sources:
                print(f"Sources:")
                seen_sources = set()
                for s in sources:
                    src_name = s.get('source', 'Unknown')
                    if src_name not in seen_sources:
                        print(f"   - {src_name} (Score: {s.get('score', 0):.4f})")
                        seen_sources.add(src_name)
            
            print("-" * 60)

        except KeyboardInterrupt:
            print(f"\n\n{GREEN}Thanks for using Hyundai Sales Buddy! Feel free to reach out if you have any other questions.{RESET}")
            break
        except Exception as e:
            print(f"\n{RED}Error: {e}{RESET}")

if __name__ == "__main__":
    main()
