# Trigger rebuild
import os
import time
import signal
import logging
from fastapi import FastAPI, Depends, HTTPException, Request
from contextlib import asynccontextmanager
import uvicorn
import redis

from .config import settings
from .auth import verify_api_key
from .rate_limiter import check_rate_limit, r
from .cost_guard import check_budget, record_usage

logging.basicConfig(level=settings.LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_in_flight_requests = 0
_is_ready = False
START_TIME = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    logger.info("Starting up...")
    _is_ready = True
    yield
    _is_ready = False
    logger.info("Graceful shutdown initiated...")
    timeout = 30
    elapsed = 0
    while _in_flight_requests > 0 and elapsed < timeout:
        logger.info(f"Waiting for {_in_flight_requests} requests...")
        time.sleep(1)
        elapsed += 1
    logger.info("Shutdown complete")

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def track_requests(request: Request, call_next):
    global _in_flight_requests
    _in_flight_requests += 1
    try:
        response = await call_next(request)
        return response
    finally:
        _in_flight_requests -= 1

@app.get("/health")
def health():
    return {"status": "ok", "uptime_seconds": time.time() - START_TIME}

@app.get("/ready")
def ready():
    if not _is_ready:
        raise HTTPException(503, "Not ready")
    try:
        r.ping()
        return {"status": "ready"}
    except Exception:
        raise HTTPException(503, "Redis not connected")

@app.post("/ask")
def ask(
    question: str,
    user_id: str = Depends(verify_api_key)
):
    check_rate_limit(user_id)
    check_budget(user_id)
    
    # Mock LLM and History
    history_key = f"history:{user_id}"
    history = r.lrange(history_key, 0, -1)
    
    answer = f"Mock Answer to: {question}"
    
    r.rpush(history_key, f"Q: {question}", f"A: {answer}")
    r.expire(history_key, 3600)
    
    record_usage(user_id)
    
    return {
        "question": question,
        "answer": answer,
        "history_len": len(history) // 2 + 1
    }

def handle_sigterm(signum, frame):
    logger.info(f"Received signal {signum}")

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, timeout_graceful_shutdown=30)
