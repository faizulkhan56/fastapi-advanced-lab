from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database directory from environment variable or use default
DB_DIR = os.getenv("DATABASE_DIR", "./data")

# Ensure database directory exists
os.makedirs(DB_DIR, exist_ok=True)

# Database file path
DB_FILE = os.path.join(DB_DIR, "test.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
