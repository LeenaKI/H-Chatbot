import streamlit as st
import os
import time

# Page Config
st.set_page_config(
    page_title="Hyundai Sales Buddy",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #f0f2f6;
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #e8f0fe;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("Hyundai Sales Buddy")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_state" not in st.session_state:
    st.session_state.session_state = {
        "conversation_history": []
    }

if "last_metrics" not in st.session_state:
    st.session_state.last_metrics = {}

if "last_sources" not in st.session_state:
    st.session_state.last_sources = []

if "keys_set" not in st.session_state:
    st.session_state.keys_set = False

# Token Input
if not st.session_state.keys_set:
    st.info("Please enter your API Keys to continue.")
    
    col1, col2 = st.columns(2)
    with col1:
        hf_token = st.text_input("Hugging Face Token", type="password")
    with col2:
        gemini_key = st.text_input("Gemini API Key", type="password")
    
    if st.button("Start Chatbot"):
        if hf_token and gemini_key:
            os.environ["HF_TOKEN"] = hf_token
            os.environ["GEMINI_API_KEY"] = gemini_key
            st.session_state.keys_set = True
            st.success("Keys set! Loading model...")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Please enter both keys.")
    st.stop()

# Import run_query ONLY after token is set to ensure lazy loading works with the token
from graph.run import run_query

# Sidebar for Metrics
with st.sidebar:
    st.header("Live Metrics")
    
    metrics = st.session_state.last_metrics
    if metrics:
        # Cost
        cost = metrics.get("cost_usd", 0.0)
        cost_inr = metrics.get("cost_inr", 0.0)
        st.metric("Cost (USD)", f"${cost:.6f}")
        st.metric("Cost (INR)", f"₹{cost_inr:.4f}")
        
        # Tokens
        total_tok = metrics.get("total_tokens", 0)
        input_tok = metrics.get("input_tokens", 0)
        output_tok = metrics.get("output_tokens", 0)
        cached_tok = metrics.get("cached_tokens", 0)
        thoughts_tok = metrics.get("thoughts_tokens", 0)
        
        st.markdown("### Token Breakdown")
        st.markdown(f"""
        - **Total**: {total_tok}
        - **Input**: {input_tok}
        - **Output**: {output_tok}
        - **Cached**: {cached_tok}
        - **Thoughts**: {thoughts_tok}
        """)
        
        # Latency
        latency = metrics.get("llm_time_ms", 0)
        st.metric("LLM Latency", f"{latency} ms")
    else:
        st.info("Run a query to see metrics.")

    st.divider()
    
    st.header("Retrieved Sources")
    sources = st.session_state.last_sources
    if sources:
        seen = set()
        for s in sources:
            src = s.get('source', 'Unknown')
            if src not in seen:
                st.caption(f"📄 {src}")
                seen.add(src)
    else:
        st.caption("No sources used.")

    if st.button("Clear History"):
        st.session_state.messages = []
        st.session_state.session_state = {"conversation_history": []}
        st.session_state.last_metrics = {}
        st.session_state.last_sources = []
        st.rerun()

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], list):
            # Render Quiz
            st.write("**Here is your quiz!**")
            for i, q in enumerate(message["content"], 1):
                st.markdown(f"**Q{i}: {q.get('question')}**")
                for opt in q.get('options', []):
                    st.text(f"  {opt}")
                st.markdown(f"*Correct Answer: {q.get('correct_answer')}*")
                if q.get('explanation'):
                    st.info(f"{q.get('explanation')}")
                st.divider()
        else:
            st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask about Hyundai cars..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Run Query
                response = run_query(prompt, st.session_state.session_state)
                
                # Update Session State History
                st.session_state.session_state["conversation_history"] = response["conversation_history"]
                
                # Update Metrics & Sources
                st.session_state.last_metrics = response.get("metrics", {})
                st.session_state.last_sources = response.get("retrieved_chunks", [])
                
                # Get Final Answer
                final_answer = response.get("final_answer", "")
                
                # Display Answer
                if isinstance(final_answer, list):
                    # Quiz Mode
                    st.write("**Here is your quiz!**")
                    for i, q in enumerate(final_answer, 1):
                        st.markdown(f"**Q{i}: {q.get('question')}**")
                        for opt in q.get('options', []):
                            st.text(f"  {opt}")
                        with st.expander(f"Show Answer for Q{i}"):
                            st.success(f"Correct Answer: {q.get('correct_answer')}")
                            if q.get('explanation'):
                                st.info(f"{q.get('explanation')}")
                    
                    st.session_state.messages.append({"role": "assistant", "content": final_answer})
                else:
                    # Text Mode
                    st.markdown(final_answer)
                    st.session_state.messages.append({"role": "assistant", "content": final_answer})
                    
                # Force rerun to update sidebar metrics immediately
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")
