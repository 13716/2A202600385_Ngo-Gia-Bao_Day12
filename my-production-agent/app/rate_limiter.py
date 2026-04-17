import time
import redis
from fastapi import HTTPException
from .config import settings

# Initialize Redis client
r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def check_rate_limit(user_id: str):
    """
    Sliding Window Rate Limiter using Redis Sorted Sets (ZSET).
    
    Logic:
    1. Key: rate_limit:<user_id>
    2. Member: current timestamp (float)
    3. Score: current timestamp (float)
    """
    now = time.time()
    key = f"rate_limit:{user_id}"
    window = 60  # 1 minute window
    limit = settings.RATE_LIMIT_PER_MINUTE

    try:
        # Create a pipeline to ensure atomicity
        pipe = r.pipeline()
        
        # 1. Remove timestamps older than the window
        pipe.zremrangebyscore(key, 0, now - window)
        
        # 2. Count current timestamps in the window
        pipe.zcard(key)
        
        # 3. Add current timestamp
        pipe.zadd(key, {str(now): now})
        
        # 4. Set expiration for the key (to cleanup unused keys)
        pipe.expire(key, window)
        
        # Execute pipeline
        _, current_count, _, _ = pipe.execute()
        
        if current_count >= limit:
            # Calculate retry after
            oldest = r.zrange(key, 0, 0, withscores=True)
            retry_after = 60
            if oldest:
                retry_after = int(oldest[0][1] + window - now) + 1
                
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": limit,
                    "retry_after_seconds": max(1, retry_after)
                }
            )
            
        return {
            "limit": limit,
            "remaining": limit - current_count - 1
        }
    except redis.ConnectionError:
        # Fallback if Redis is down (optional: log error and allow request or deny)
        print("⚠️ Redis Connection Error - Bypassing rate limit")
        return {"limit": limit, "remaining": -1}
