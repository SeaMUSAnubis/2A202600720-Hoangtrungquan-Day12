import redis
import time
from datetime import datetime
from fastapi import HTTPException
from .config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

PRICE_PER_REQUEST = 0.01  # Mock price

def check_budget(user_id: str):
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    current = float(r.get(key) or 0)
    if current >= settings.MONTHLY_BUDGET_USD:
        raise HTTPException(status_code=402, detail="Monthly budget exceeded")

def record_usage(user_id: str):
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    r.incrbyfloat(key, PRICE_PER_REQUEST)
    r.expire(key, 32 * 24 * 3600)
