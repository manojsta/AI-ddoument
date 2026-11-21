from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pgvector.sqlalchemy import Vector
from sqlalchemy import text
from .config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def init_db():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    from . import models  # noqa
    Base.metadata.create_all(bind=engine)
    # Backward-compatible migration: existing accounts remain usable; newly-created
    # accounts are explicitly marked for mandatory first-login setup in the API.
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN NOT NULL DEFAULT FALSE"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS security_setup_complete BOOLEAN NOT NULL DEFAULT TRUE"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
