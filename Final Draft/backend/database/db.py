"""
Database connection and session management

This module sets up the SQLAlchemy database engine and session factory for the SQLite database.
It also provides:
  - init_db(): called on app startup to create all tables if they don't exist
  - get_db(): a FastAPI dependency that provides a database session to each request
               and ensures the session is closed after the request completes
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base
from pathlib import Path

# ─── Database File Location ─────────────────────────────────────────────────────────
# Build the absolute path to the SQLite database file (stored at project_root/data/app.db)
# __file__ refers to this db.py file; .parent.parent.parent walks up to the project root
DB_PATH = Path(__file__).parent.parent.parent / "data" / "app.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)  # Create the /data/ directory if it doesn't exist

# ─── SQLAlchemy Engine ───────────────────────────────────────────────────────────
# The engine manages the connection to the SQLite file.
# 'check_same_thread=False' is required for SQLite when used with FastAPI/async frameworks
# because multiple request threads may share the same connection.
DATABASE_URL = f"sqlite:///{DB_PATH}"  # SQLite connection string pointing to our .db file
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# ─── Session Factory ────────────────────────────────────────────────────────────
# SessionLocal is a factory that creates new database session objects on demand.
# autocommit=False means changes aren't saved until you explicitly call db.commit()
# autoflush=False means SQLAlchemy won't automatically send pending changes to the DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database initialized at: {DB_PATH}")

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
