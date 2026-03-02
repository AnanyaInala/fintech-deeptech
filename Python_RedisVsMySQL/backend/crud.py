"""
crud.py - CRUD Operations (Create, Read, Update, Delete)

This file contains all database operations separated from the API routes.
This separation follows the "Repository Pattern" - keeping data access logic
separate from API logic makes the code cleaner and more testable.
"""

from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, UserUpdate
from typing import Optional


# ─── CREATE ────────────────────────────────────────────────────────────

def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user in the MySQL database.
    
    Steps:
    1. Convert Pydantic schema to SQLAlchemy model
    2. Add to session (staging area)
    3. Commit (save to database)
    4. Refresh (reload from DB to get auto-generated fields like id)
    
    Args:
        db: Database session
        user_data: Validated user data from the API request
        
    Returns:
        User: The newly created user with all fields populated
    """
    # Create a SQLAlchemy User object from the Pydantic schema
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        age=user_data.age
    )
    
    db.add(db_user)           # Stage the new user
    db.commit()               # Save to MySQL
    db.refresh(db_user)       # Reload to get the auto-generated id and created_at
    
    return db_user


# ─── READ ──────────────────────────────────────────────────────────────

def get_all_users(db: Session) -> list:
    """
    Fetch ALL users from MySQL database.
    Equivalent SQL: SELECT * FROM users ORDER BY id DESC;
    
    Returns:
        list: List of User objects
    """
    return db.query(User).order_by(User.id.desc()).all()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Fetch a single user by their ID.
    Equivalent SQL: SELECT * FROM users WHERE id = ? LIMIT 1;
    
    Returns:
        User or None: The user if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Fetch a single user by their email.
    Useful for checking if an email already exists.
    
    Returns:
        User or None: The user if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()


# ─── UPDATE ────────────────────────────────────────────────────────────

def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """
    Update an existing user's information.
    Only updates fields that are provided (partial update).
    
    Steps:
    1. Find the user
    2. Update only the provided fields
    3. Commit changes
    4. Return the updated user
    
    Returns:
        User or None: Updated user if found, None otherwise
    """
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        return None
    
    # model_dump(exclude_unset=True) gives us only the fields the client sent
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_user, field, value)    # Dynamically set each attribute
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


# ─── DELETE ────────────────────────────────────────────────────────────

def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user from the database.
    
    Returns:
        bool: True if user was deleted, False if user not found
    """
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    
    return True
