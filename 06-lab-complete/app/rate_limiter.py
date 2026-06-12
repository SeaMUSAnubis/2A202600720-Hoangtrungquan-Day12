import redis
from fastapi import HTTPException
from .config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def check_rate_limit(user_id: str):
    import time
    current_minute = int(time.time() / 60)
    key = f"rate_limit:{user_id}:{current_minute}"
    
    current = r.get(key)
    if current and int(current) >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Too Many Requests")
    
    pipe = r.pipeline()
    pipe.incr(key)
    pipe.expire(key, 120)
    pipe.execute()
