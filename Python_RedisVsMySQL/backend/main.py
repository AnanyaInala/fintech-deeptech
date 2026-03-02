"""
main.py - FastAPI Application Entry Point

This is the heart of the backend. It defines all the API endpoints (routes)
and connects everything together: Database, Redis Cache, CRUD operations.

Run with: uvicorn main:app --reload --port 8000
"""

import time
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from schemas import UserCreate, UserUpdate, UserResponse, MessageResponse
from crud import create_user, get_all_users, get_user_by_id, get_user_by_email, update_user, delete_user
from redis_cache import get_cached_users, set_cached_users, clear_cache, get_cache_info

# ─── Create Database Tables ───────────────────────────────────────────
# This creates all tables defined in models.py if they don't exist yet.
# In production, you'd use Alembic migrations instead.
Base.metadata.create_all(bind=engine)

# ─── Initialize FastAPI App ───────────────────────────────────────────
app = FastAPI(
    title="Redis vs MySQL - User Management API",
    description="A teaching API to demonstrate Redis caching performance vs direct MySQL queries.",
    version="1.0.0"
)

# ─── CORS Middleware ───────────────────────────────────────────────────
# CORS (Cross-Origin Resource Sharing) allows the React frontend
# (running on port 3000) to make requests to this API (port 8000).
# Without this, the browser would BLOCK all requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins (restrict in production!)
    allow_credentials=True,
    allow_methods=["*"],          # Allow all HTTP methods
    allow_headers=["*"],          # Allow all headers
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                          API ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# ─── Health Check ──────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """Health check endpoint. Verify the API is running."""
    return {
        "status": "running",
        "message": "Redis vs MySQL API is live! Visit /docs for Swagger UI."
    }


# ─── DEMO ENDPOINT (No Database Required) ─────────────────────────────

@app.get("/demo/users", tags=["Demo"])
def demo_users():
    """
    Demo endpoint with sample data (No database required).
    Use this to test the frontend even if MySQL is down.
    """
    sample_users = [
        {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "age": 28, "created_at": "2024-01-15T10:30:00"},
        {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "age": 34, "created_at": "2024-01-16T14:20:00"},
        {"id": 3, "name": "Charlie Brown", "email": "charlie@example.com", "age": 22, "created_at": "2024-01-17T09:45:00"},
        {"id": 4, "name": "Diana Prince", "email": "diana@example.com", "age": 30, "created_at": "2024-01-18T16:10:00"},
        {"id": 5, "name": "Edward Norton", "email": "edward@example.com", "age": 45, "created_at": "2024-01-19T11:55:00"},
    ]
    return {
        "source": "demo",
        "cache_status": "CACHED (Demo)",
        "response_time_ms": 5.2,
        "total_users": len(sample_users),
        "users": sample_users,
        "note": "This is demo data. Connect to MySQL for real data."
    }


# ─── CREATE USER ──────────────────────────────────────────────────────

@app.post("/users", response_model=UserResponse, tags=["Users"])
def api_create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    
    Steps:
    1. Check if email already exists (prevent duplicates)
    2. Create user in MySQL
    3. Clear Redis cache (so next fetch gets fresh data)
    4. Return the new user
    """
    # Check for duplicate email
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail=f"Email '{user.email}' is already registered."
        )
    
    # Create the user in MySQL
    new_user = create_user(db, user)
    
    # Clear the Redis cache (data has changed!)
    clear_cache()
    
    return new_user


# ─── GET ALL USERS (Direct MySQL) ─────────────────────────────────────

@app.get("/users/mysql", tags=["Users"])
def api_get_users_mysql(db: Session = Depends(get_db)):
    """
    Fetch ALL users directly from MySQL (no caching).
    
    This endpoint always hits the database, which is slower but
    guarantees the most up-to-date data.
    
    Use this to compare performance with the Redis endpoint.
    """
    start_time = time.time()
    
    users = get_all_users(db)
    
    elapsed_ms = round((time.time() - start_time) * 1000, 2)
    
    # Convert SQLAlchemy objects to dictionaries for JSON response
    users_list = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "age": u.age,
            "created_at": str(u.created_at) if u.created_at else None
        }
        for u in users
    ]
    
    return {
        "source": "mysql",
        "cache_status": "N/A",
        "response_time_ms": elapsed_ms,
        "total_users": len(users_list),
        "users": users_list
    }


# ─── GET ALL USERS (Redis Cache) ──────────────────────────────────────

@app.get("/users/redis", tags=["Users"])
def api_get_users_redis(db: Session = Depends(get_db)):
    """
    Fetch ALL users with Redis caching.
    
    Flow:
    1. Check Redis cache first
    2. If CACHE HIT  → return cached data (super fast!)
    3. If CACHE MISS → fetch from MySQL, store in Redis, then return
    
    The cache expires after 60 seconds (TTL).
    """
    start_time = time.time()
    
    # Step 1: Try Redis first
    cached_users = get_cached_users()
    
    if cached_users is not None:
        # ✅ CACHE HIT - Data found in Redis!
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "source": "redis",
            "cache_status": "HIT",
            "response_time_ms": elapsed_ms,
            "total_users": len(cached_users),
            "users": cached_users
        }
    
    # ❌ CACHE MISS - Need to fetch from MySQL
    users = get_all_users(db)
    
    users_list = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "age": u.age,
            "created_at": str(u.created_at) if u.created_at else None
        }
        for u in users
    ]
    
    # Store in Redis for next time
    set_cached_users(users_list)
    
    elapsed_ms = round((time.time() - start_time) * 1000, 2)
    
    return {
        "source": "mysql → redis",
        "cache_status": "MISS",
        "response_time_ms": elapsed_ms,
        "total_users": len(users_list),
        "users": users_list
    }


# ─── GET SINGLE USER ──────────────────────────────────────────────────

@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def api_get_user(user_id: int, db: Session = Depends(get_db)):
    """Fetch a single user by their ID."""
    user = get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found."
        )
    
    return user


# ─── UPDATE USER ──────────────────────────────────────────────────────

@app.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def api_update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user's information.
    Clears Redis cache after update to prevent stale data.
    """
    updated_user = update_user(db, user_id, user)
    
    if not updated_user:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found."
        )
    
    # Clear cache since data changed
    clear_cache()
    
    return updated_user


# ─── DELETE USER ──────────────────────────────────────────────────────

@app.delete("/users/{user_id}", tags=["Users"])
def api_delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by their ID.
    Clears Redis cache after deletion.
    """
    success = delete_user(db, user_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found."
        )
    
    # Clear cache since data changed
    clear_cache()
    
    return {"message": f"User {user_id} deleted successfully."}


# ─── CACHE INFO ───────────────────────────────────────────────────────

@app.get("/cache/info", tags=["Cache"])
def api_cache_info():
    """Get current Redis cache status (for debugging)."""
    return get_cache_info()


@app.delete("/cache/clear", tags=["Cache"])
def api_clear_cache():
    """Manually clear the Redis cache."""
    clear_cache()
    return {"message": "Cache cleared successfully."}
