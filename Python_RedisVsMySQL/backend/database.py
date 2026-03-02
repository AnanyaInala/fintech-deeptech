"""
database.py - MySQL Database Connection & Session Management
Uses SQLAlchemy ORM to connect to a local MySQL database.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ─── MySQL Connection String ───────────────────────────────────────────
# Format: mysql+pymysql://username:password@host/database_name
DATABASE_URL = "mysql+pymysql://root:root@localhost/MRUMRECW"
# Note: '@' in the password is URL-encoded as '%40'

# ─── Create the SQLAlchemy Engine ──────────────────────────────────────
# The engine is the starting point for any SQLAlchemy application.
# It manages database connections for us.
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Number of persistent connections in the pool
    max_overflow=20,       # Extra connections allowed beyond pool_size
    pool_pre_ping=True,    # Test connections before using them (avoids stale connections)
    echo=False             # Set to True to see raw SQL queries in the console (useful for debugging)
)

# ─── Create a Session Factory ─────────────────────────────────────────
# A session is like a "workspace" for our database operations.
# autocommit=False: We manually control when data is saved.
# autoflush=False:  We manually control when data is sent to the DB.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ─── Declare a Base Class for Models ──────────────────────────────────
# All our database models (tables) will inherit from this Base class.
Base = declarative_base()


def get_db():
    """
    Dependency function that provides a database session.
    
    How it works:
    1. Creates a new database session.
    2. Gives it to the endpoint function (via `yield`).
    3. Automatically closes the session when the request is done.
    
    Usage in FastAPI:
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
