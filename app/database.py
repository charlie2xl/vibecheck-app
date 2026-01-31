from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import DATABASE_URL
from app.models import Base

# Create database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Database session dependency.
    """
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


def initialize_database():
    """
    Initialize database by creating all tables.
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
