import os
from pathlib import Path
import uuid

import pytest
from fastapi.testclient import TestClient

os.environ['DATABASE_URL'] = 'sqlite:///./test_s1.db'
os.environ['ASSETS_DIR'] = 'app/assets/test_generated'
os.environ['ASSET_STORAGE_BACKEND'] = 'local'

from app.core.config import get_settings  # noqa: E402

get_settings.cache_clear()

from app.db.base import Base  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope='session', autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    db_path = Path('test_s1.db')
    if db_path.exists():
        try:
            db_path.unlink()
        except PermissionError:
            pass


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def register_and_login(client: TestClient) -> str:
    email = f'test{uuid.uuid4().hex[:8]}@example.com'
    password = 'supersecret123'
    reg = client.post(
        '/api/v1/auth/register',
        json={'email': email, 'full_name': 'Test Bruker', 'password': password},
    )
    reg.raise_for_status()

    response = client.post(
        '/api/v1/auth/login',
        data={'username': email, 'password': password},
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    response.raise_for_status()
    return response.json()['access_token']


@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    token = register_and_login(client)
    return {'Authorization': f'Bearer {token}'}

