from collections.abc import Generator
import re

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql.psycopg import PGDialect_psycopg
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

_original_version_parser = PGDialect_psycopg._get_server_version_info


def _parse_server_version(self, connection):
    try:
        return _original_version_parser(self, connection)
    except AssertionError:
        version = connection.exec_driver_sql("select version()").scalar() or ""
        match = re.search(r"openGauss\s+(\d+)\.(\d+)(?:\.(\d+))?", version)
        if match:
            major, minor, patch = match.groups(default="0")
            return int(major), int(minor), int(patch)
        raise


PGDialect_psycopg._get_server_version_info = _parse_server_version

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
