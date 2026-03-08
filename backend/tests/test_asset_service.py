import os
from pathlib import Path

import matplotlib.pyplot as plt

from app.core.config import get_settings
from app.services.asset_service import AssetService


class _FakeS3Client:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def put_object(self, **kwargs):
        self.calls.append(kwargs)


def test_asset_service_local_storage(tmp_path, monkeypatch):
    monkeypatch.setenv('ASSET_STORAGE_BACKEND', 'local')
    monkeypatch.setenv('ASSETS_DIR', str(tmp_path))
    monkeypatch.setenv('ASSETS_LOCAL_URL_PREFIX', '/assets')
    get_settings.cache_clear()

    service = AssetService()

    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    url = service.save_figure(fig, 'test')

    assert url.startswith('/assets/test_')
    filename = url.split('/')[-1]
    assert (Path(tmp_path) / filename).exists()


def test_asset_service_s3_storage(monkeypatch):
    monkeypatch.setenv('ASSET_STORAGE_BACKEND', 's3')
    monkeypatch.setenv('S3_BUCKET_NAME', 'bucket')
    monkeypatch.setenv('S3_KEY_PREFIX', 'generated')
    monkeypatch.setenv('ASSETS_PUBLIC_BASE_URL', 'https://cdn.example.com/math-assets')
    monkeypatch.delenv('ASSETS_DIR', raising=False)
    get_settings.cache_clear()

    service = AssetService()
    fake_client = _FakeS3Client()
    service._s3_client = fake_client

    fig, ax = plt.subplots()
    ax.plot([0, 1], [1, 2])
    url = service.save_figure(fig, 'graph')

    assert url.startswith('https://cdn.example.com/math-assets/generated/graph_')
    assert len(fake_client.calls) == 1
    call = fake_client.calls[0]
    assert call['Bucket'] == 'bucket'
    assert call['Key'].startswith('generated/graph_')
    assert call['ContentType'] == 'image/png'
    assert call['CacheControl'].startswith('public')
    assert isinstance(call['Body'], (bytes, bytearray))

    # reset global env cache for other tests
    os.environ['ASSET_STORAGE_BACKEND'] = 'local'
    get_settings.cache_clear()
