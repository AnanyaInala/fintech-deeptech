"""
models.py - SQLAlchemy Database Models
Defines the structure of our database tables using Python classes.
Each class = one table in MySQL.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """
    User model - Maps to the 'users' table in MySQL.
    
    Think of this class as a blueprint for each row in the 'users' table.
    Each attribute (Column) represents a column in the table.
    """
    
    __tablename__ = "users"  # The actual table name in MySQL

    # ─── Columns ───────────────────────────────────────────────────────
    id = Column(
        Integer,
        primary_key=True,       # This is the unique identifier
        index=True,             # Create an index for faster lookups
        autoincrement=True      # MySQL auto-generates IDs (1, 2, 3, ...)
    )
    
    name = Column(
        String(100),            # VARCHAR(100) in MySQL
        nullable=False          # This field is required (cannot be NULL)
    )
    
    email = Column(
        String(100),            # VARCHAR(100) in MySQL
        unique=True,            # No two users can have the same email
        nullable=False,         # This field is required
        index=True              # Index for faster email lookups
    )
    
    age = Column(
        Integer,                # INT in MySQL
        nullable=False          # This field is required
    )
    
    created_at = Column(
        DateTime(timezone=True),           # DATETIME in MySQL
        server_default=func.now()          # Auto-set to current timestamp when created
    )

    def __repr__(self):
        """String representation for debugging."""
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
