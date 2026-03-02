"""
schemas.py - Pydantic Schemas (Data Validation & Serialization)

Pydantic schemas are NOT database models. They define:
  1. What data the API ACCEPTS (request body validation)
  2. What data the API RETURNS (response serialization)

Think of schemas as "contracts" for your API.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ─── Request Schemas (What the client sends) ───────────────────────────

class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    When a client sends a POST request, the data must match this shape.
    
    Example JSON body:
    {
        "name": "Alice",
        "email": "alice@example.com",
        "age": 25
    }
    """
    name: str = Field(
        ...,                          # Required field (no default value)
        min_length=1,                 # At least 1 character
        max_length=100,               # At most 100 characters
        examples=["Alice Johnson"]    # Example for auto-generated docs
    )
    email: str = Field(
        ...,
        min_length=5,
        max_length=100,
        examples=["alice@example.com"]
    )
    age: int = Field(
        ...,
        ge=1,                         # Greater than or equal to 1
        le=150,                       # Less than or equal to 150
        examples=[25]
    )


class UserUpdate(BaseModel):
    """
    Schema for updating a user.
    All fields are optional - only send what you want to change.
    
    Example JSON body (partial update):
    {
        "name": "Alice Smith"
    }
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, min_length=5, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=150)


# ─── Response Schemas (What the server returns) ───────────────────────

class UserResponse(BaseModel):
    """
    Schema for returning user data to the client.
    Includes the database-generated fields (id, created_at).
    """
    id: int
    name: str
    email: str
    age: int
    created_at: Optional[datetime] = None

    class Config:
        """
        Config tells Pydantic how to behave.
        from_attributes = True: Allows Pydantic to read data from SQLAlchemy model
                                objects (not just dictionaries).
        """
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic response for messages (success, error, etc.)."""
    message: str
    source: Optional[str] = None    # "mysql", "redis", etc.
