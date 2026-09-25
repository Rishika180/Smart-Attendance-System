"""
Database setup for the Smart Attendance System.

Uses SQLite for simplicity (zero external setup) via SQLAlchemy's ORM.
The database file (attendance.db) is created automatically in the
backend/ directory the first time the app runs.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./attendance.db"

# check_same_thread=False is required because FastAPI can use the
# connection from more than one worker thread.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
