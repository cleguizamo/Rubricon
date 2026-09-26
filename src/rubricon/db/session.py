""" Database engine and session management. """

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from rubricon.config import get_settings


class Base(DeclarativeBase):
    pass

engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    """FastAPY dependecy: one session per request, always closed"""

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()