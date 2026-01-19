from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from graph.run import run_query

app = FastAPI(title="Hyundai Sales Buddy API")

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"
    history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    answer: Any # Can be str (normal) or List[Dict] (quiz)
    sources: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    history: List[Dict[str, str]]

# In-memory session store
sessions: Dict[str, Dict] = {}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Retrieve or initialize session state
        if request.session_id not in sessions:
            sessions[request.session_id] = {"conversation_history": request.history or []}
        
        session_state = sessions[request.session_id]
        
        # Run the graph
        result = run_query(request.query, session_state)
        
        # Update session history
        sessions[request.session_id]["conversation_history"] = result.get("conversation_history", [])
        
        return ChatResponse(
            answer=result.get("final_answer", "No answer generated."),
            sources=result.get("sources", []),
            metrics=result.get("metrics", {}),
            history=result.get("conversation_history", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
