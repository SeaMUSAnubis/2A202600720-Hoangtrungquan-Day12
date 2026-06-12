import time
import logging
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, List
import asyncio
from agent_orchestrator import run_workflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_in_flight_requests = 0
_is_ready = False
START_TIME = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    logger.info("Backend is starting up...")
    _is_ready = True
    yield
    _is_ready = False
    logger.info("Graceful shutdown initiated...")
    timeout = 30
    elapsed = 0
    while _in_flight_requests > 0 and elapsed < timeout:
        logger.info(f"Waiting for {_in_flight_requests} in-flight requests...")
        await asyncio.sleep(1)
        elapsed += 1
    logger.info("Shutdown complete")

app = FastAPI(title="Legal AI Hub API", lifespan=lifespan)

@app.middleware("http")
async def track_requests(request: Request, call_next):
    global _in_flight_requests
    _in_flight_requests += 1
    try:
        response = await call_next(request)
        return response
    finally:
        _in_flight_requests -= 1

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "uptime_seconds": time.time() - START_TIME}

@app.get("/ready")
def ready():
    if not _is_ready:
        raise HTTPException(503, "Not ready")
    return {"status": "ready"}

@app.get("/")
def read_root():
    return {"message": "Legal AI Backend is running. Please use the frontend to interact, or send POST to /api/chat"}

class ChatRequest(BaseModel):
    query: str

class Citation(BaseModel):
    id: int
    title: str
    score: str
    content: str

class AgentResponse(BaseModel):
    agentType: str
    text: str
    citations: Optional[List[Citation]] = None

@app.post("/api/chat", response_model=AgentResponse)
async def chat(request: ChatRequest, x_api_key: Optional[str] = Header(None)):
    """
    Sử dụng LangGraph StateGraph để xử lý câu hỏi với đa tác nhân.
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API Key. Vui lòng cung cấp OpenRouter API Key qua giao diện cài đặt.")

    query = request.query
    
    # Run the multi-agent workflow
    final_state = await run_workflow(query, api_key=x_api_key)
    
    # Gộp các câu trả lời từ các agents (bỏ qua HumanMessage đầu tiên)
    agent_messages = [msg.content for msg in final_state["messages"][1:]]
    combined_response = "\n\n".join(agent_messages)
    
    # Simple mock response in case of no agent matched
    if not combined_response:
        combined_response = f"Tôi không có đủ thông tin để tư vấn về: {query}"
        
    return AgentResponse(
        agentType="customer",
        text=combined_response,
        citations=[
            Citation(id=1, title='Điều 249 Bộ luật Hình sự 2015', score='0.92', content='Tội tàng trữ trái phép chất ma túy...')
        ]
    )

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
