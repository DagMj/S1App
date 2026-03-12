import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _normalize_database_url(raw_url: str | None) -> str:
    value = (raw_url or '').strip()
    if not value:
        logger.warning('DATABASE_URL is empty. Falling back to local sqlite.')
        return 'sqlite:///./s1_mvp.db'

    if value.startswith('${{') and value.endswith('}}'):
        logger.warning('DATABASE_URL appears unresolved (%s). Falling back to local sqlite.', value)
        return 'sqlite:///./s1_mvp.db'

    if value.startswith('postgresql+psycopg://'):
        return value
    if value.startswith('postgres://'):
        return 'postgresql+psycopg://' + value[len('postgres://'):]
    if value.startswith('postgresql://'):
        return 'postgresql+psycopg://' + value[len('postgresql://'):]
    return value


def _build_engine(url: str):
    if url.startswith('sqlite'):
        connect_args = {'check_same_thread': False}
    else:
        # connect_timeout (seconds) ensures each failed attempt times out quickly
        # instead of hanging on the TCP default (~75s). With 12 retries at 1.5s
        # sleep, worst-case DB wait is 12 * (5 + 1.5) ≈ 78s — within Railway's
        # 120s health-check window even if the DB is temporarily unavailable.
        connect_args = {'connect_timeout': 5}
    engine_kwargs = {
        'future': True,
        'echo': False,
        'connect_args': connect_args,
    }
    if not url.startswith('sqlite'):
        engine_kwargs['pool_pre_ping'] = True
    return create_engine(url, **engine_kwargs)


database_url = _normalize_database_url(settings.database_url)

try:
    engine = _build_engine(database_url)
except Exception as exc:  # pragma: no cover
    logger.exception('Failed to initialize DB engine for DATABASE_URL=%s: %s', database_url, exc)
    database_url = 'sqlite:///./s1_mvp.db'
    engine = _build_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
