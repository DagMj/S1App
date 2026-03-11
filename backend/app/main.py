import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.api.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.generators.library import register_all_generators
from app.services.generator_registry_service import registry_service

logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version='0.1.0',
    docs_url='/docs',
    redoc_url='/redoc',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

assets_abs = settings.assets_dir.resolve()
assets_abs.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.assets_local_url_prefix,
    StaticFiles(directory=str(assets_abs)),
    name='assets',
)


def _wait_for_database(max_attempts: int = 12, sleep_seconds: float = 1.5) -> None:
    last_error: Exception | None = None
    for _ in range(max_attempts):
        try:
            with engine.connect() as conn:
                conn.execute(text('SELECT 1'))
            return
        except Exception as exc:  # pragma: no cover
            last_error = exc
            time.sleep(sleep_seconds)
    if last_error is not None:
        raise last_error


@app.on_event('startup')
def on_startup() -> None:
    app.state.db_ready = False

    try:
        register_all_generators()
        _wait_for_database()
        if settings.reset_db:
            logger.warning('RESET_DB=true: dropping and recreating all tables')
            Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            registry_service.ensure_registered_in_db(db)
        finally:
            db.close()
        app.state.db_ready = True
    except Exception as exc:  # pragma: no cover
        logger.exception('Database init failed during startup, running in degraded mode: %s', exc)


@app.get('/health')
def health() -> dict:
    return {
        'status': 'ok',
        'version': 'v1',
        'db_ready': bool(getattr(app.state, 'db_ready', False)),
    }


@app.get('/')
def root() -> dict:
    return {'status': 'ok'}


app.include_router(api_router, prefix=settings.api_prefix)
