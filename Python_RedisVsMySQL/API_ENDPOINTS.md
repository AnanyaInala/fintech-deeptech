# Redis vs MySQL - API Endpoints

## System Status
✅ **MySQL**: Running (root:root@localhost/MRUMRECW)  
✅ **Redis**: Running (localhost:6379)  
✅ **Backend**: Running (http://localhost:8000)  
✅ **Frontend**: Running (http://localhost:3000)

---

## Available Endpoints

### 1. **Health Check** (Works Anytime)
```
GET http://localhost:8000/
```
**Response:**
```json
{
  "status": "running",
  "message": "Redis vs MySQL API is live! Visit /docs for Swagger UI."
}
```

---

### 2. **Demo Endpoint** (No Database Required) ⭐
```
GET http://localhost:8000/demo/users
```
**Use this if MySQL is down!**
Returns sample data with proper caching demonstration.

**Response:**
```json
{
  "source": "demo",
  "cache_status": "CACHED (Demo)",
  "response_time_ms": 5.2,
  "total_users": 5,
  "users": [
    {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "age": 28,
      "created_at": "2024-01-15T10:30:00"
    }
    // ... more users
  ]
}
```

---

### 3. **MySQL Direct Query** (Database Required)
```
GET http://localhost:8000/users/mysql
```
**What it does:**
- Queries database directly (no caching)
- Always gets fresh data
- Slower response time

**Response:**
```json
{
  "source": "mysql",
  "cache_status": "N/A",  ← This is because MySQL endpoint doesn't use Redis
  "response_time_ms": 45.3,
  "total_users": 5,
  "users": [...]
}
```

**Why cache_status is "N/A":**
- This endpoint intentionally bypasses Redis
- It's used to compare performance with Redis-cached queries
- MySQL always goes directly to the database

---

### 4. **Redis Cached Query** (Database + Redis Required)
```
GET http://localhost:8000/users/redis
```
**What it does:**
1. Checks Redis cache first (very fast)
2. If **CACHE HIT** → returns cached data (~1-5ms)
3. If **CACHE MISS** → queries MySQL, stores in Redis, returns (~40-50ms)

**Response on CACHE HIT:**
```json
{
  "source": "redis",
  "cache_status": "HIT",  ← Data came from Redis cache!
  "response_time_ms": 3.2,
  "total_users": 5,
  "users": [...]
}
```

**Response on CACHE MISS:**
```json
{
  "source": "mysql → redis",
  "cache_status": "MISS",  ← Had to fetch from database
  "response_time_ms": 42.8,
  "total_users": 5,
  "users": [...]
}
```

---

### 5. **Create User** (Database Required)
```
POST http://localhost:8000/users
Content-Type: application/json

{
  "name": "New User",
  "email": "newuser@example.com",
  "age": 25
}
```
**Effect:** Creates user in MySQL AND clears Redis cache

---

### 6. **Get Single User** (Database Required)
```
GET http://localhost:8000/users/{user_id}
```
Example: `GET http://localhost:8000/users/1`

---

### 7. **Update User** (Database Required)
```
PUT http://localhost:8000/users/{user_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "email": "updated@example.com",
  "age": 30
}
```
**Effect:** Updates user in MySQL AND clears Redis cache

---

### 8. **Delete User** (Database Required)
```
DELETE http://localhost:8000/users/{user_id}
```
Example: `DELETE http://localhost:8000/users/1`

**Effect:** Deletes user from MySQL AND clears Redis cache

---

### 9. **Cache Info** (Works Anytime)
```
GET http://localhost:8000/cache/info
```
Shows current Redis cache status and info

---

### 10. **Clear Cache** (Redis Required)
```
DELETE http://localhost:8000/cache/clear
```
Manually clear Redis cache

---

## Understanding Cache Status

| Endpoint | Cache Status | Meaning |
|----------|--------------|---------|
| `/users/mysql` | `N/A` | This endpoint doesn't use caching - always goes to database |
| `/users/redis` | `HIT` | Data found in Redis cache (FAST) |
| `/users/redis` | `MISS` | Data not cached, fetched from MySQL (SLOWER) |
| `/demo/users` | `CACHED (Demo)` | Demo data that works without database |

---

## Testing Without Database

**If MySQL is down, use the demo endpoint:**
```
GET http://localhost:8000/demo/users
```

**If Redis is down:**
- `/users/mysql` still works (doesn't need Redis)
- `/users/redis` falls back to MySQL (shows MISS every time)

**If both MySQL and Redis are down:**
- Use `/` (health check)
- Use `/demo/users` (demo data)

---

## Performance Comparison

Test both endpoints and compare response times:

1. **First request to `/users/redis`** → MISS (~40-50ms) - hits MySQL
2. **Second request to `/users/redis`** → HIT (~1-5ms) - hits Redis cache
3. **Any request to `/users/mysql`** → ~40-50ms - always hits MySQL

Redis is **8-50x faster** on cache hits!

