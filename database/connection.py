# database/connection.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_PATH
from database.models import Base

# Create SQLite database connection
engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)


def init_db():
    """Create all tables in the database"""
    Base.metadata.create_all(engine)
    print(f"✓ Database initialized at {DB_PATH}")


def get_session():
    """Get a new database session for queries"""
    return Session()