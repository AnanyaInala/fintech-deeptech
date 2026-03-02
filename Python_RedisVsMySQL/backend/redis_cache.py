"""
redis_cache.py - Redis Cache Manager

Redis is an in-memory data store (like a super-fast dictionary).
We use it to CACHE database results so we don't hit MySQL for every request.

Flow:
  1. Client requests data
  2. Check Redis first (very fast, ~1ms)
  3. If found in Redis → return immediately (CACHE HIT)
  4. If NOT found in Redis → query MySQL, store result in Redis, then return (CACHE MISS)
"""

import redis
import json
from typing import Optional

# ─── Redis Connection ──────────────────────────────────────────────────
# Connect to the local Redis server (default port: 6379)
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,                  # Redis supports multiple databases (0-15)
    decode_responses=True  # Auto-decode bytes to strings (makes life easier)
)

# ─── Cache Configuration ──────────────────────────────────────────────
CACHE_KEY = "all_users"        # The key under which we store user data
CACHE_TTL = 60                 # Time-To-Live: 60 seconds (cache expires after this)


def get_cached_users() -> Optional[list]:
    """
    Try to get users from Redis cache.
    
    Returns:
        list: List of user dictionaries if cache HIT
        None: If cache MISS (data not in Redis or expired)
    """
    try:
        cached_data = redis_client.get(CACHE_KEY)
        
        if cached_data:
            # Cache HIT! Data was found in Redis
            print("✅ CACHE HIT - Returning data from Redis")
            return json.loads(cached_data)  # Convert JSON string back to Python list
        else:
            # Cache MISS - Data not found (or TTL expired)
            print("❌ CACHE MISS - Data not in Redis")
            return None
            
    except redis.ConnectionError:
        print("⚠️ Redis connection failed - falling back to MySQL")
        return None


def set_cached_users(users_data: list) -> bool:
    """
    Store users data in Redis with a TTL (expiration time).
    
    Args:
        users_data: List of user dictionaries to cache
        
    Returns:
        bool: True if cached successfully, False otherwise
    """
    try:
        # Convert Python list to JSON string and store in Redis
        json_data = json.dumps(users_data, default=str)  # default=str handles datetime
        redis_client.setex(
            CACHE_KEY,      # Key name
            CACHE_TTL,      # Time-to-live in seconds
            json_data       # Value (JSON string)
        )
        print(f"📦 Cached {len(users_data)} users in Redis (TTL: {CACHE_TTL}s)")
        return True
        
    except redis.ConnectionError:
        print("⚠️ Redis connection failed - data NOT cached")
        return False


def clear_cache() -> bool:
    """
    Clear the users cache from Redis.
    
    IMPORTANT: Call this whenever data is MODIFIED (Create, Update, Delete)
    to prevent stale data from being served.
    
    Returns:
        bool: True if cache cleared, False otherwise
    """
    try:
        redis_client.delete(CACHE_KEY)
        print("🗑️ Redis cache CLEARED")
        return True
        
    except redis.ConnectionError:
        print("⚠️ Redis connection failed - cache NOT cleared")
        return False


def get_cache_info() -> dict:
    """
    Get information about the current cache state.
    Useful for debugging and monitoring.
    
    Returns:
        dict: Cache status information
    """
    try:
        ttl = redis_client.ttl(CACHE_KEY)    # Remaining TTL in seconds
        exists = redis_client.exists(CACHE_KEY)
        
        return {
            "cache_exists": bool(exists),
            "ttl_remaining": ttl if ttl > 0 else 0,
            "cache_key": CACHE_KEY,
            "max_ttl": CACHE_TTL
        }
        
    except redis.ConnectionError:
        return {
            "cache_exists": False,
            "error": "Redis connection failed"
        }
