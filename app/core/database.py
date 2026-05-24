from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.APP_ENV == "development"
)

SessionLocal = sessionmaker(
    bind= engine,
    autocommit = False,
    autoflush= False,
    expire_on_commit= False
)

def get_db() -> Session:
    """FastAPI dependency — yields one DB session per request."""
    
    db = SessionLocal()

    try:
        yield db
        
    finally:

        db.close()