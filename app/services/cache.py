"""
Redis caching service with graceful fallback
"""
import json
from typing import Optional, Any
from app.config import get_settings

settings = get_settings()

class CacheService:
    def __init__(self):
        self.redis_client: Optional[Any] = None
        self.redis_available = False
    
    async def connect(self):
        """Connect to Redis - gracefully fail if not available"""
        try:
            import redis.asyncio as redis
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2
            )
            # Test connection
            await self.redis_client.ping()
            self.redis_available = True
            print("Redis connected successfully")
        except Exception as e:
            print(f" Redis not available: {e}")
            print("   Cache will be disabled (app will still work)")
            self.redis_client = None
            self.redis_available = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_available or not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache"""
        if not self.redis_available or not self.redis_client:
            return
        
        try:
            ttl = ttl or settings.CACHE_TTL_SECONDS
            serialized = json.dumps(value, default=str)
            await self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            print(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis_available or not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")

# Global cache service instance
cache_service = CacheService()