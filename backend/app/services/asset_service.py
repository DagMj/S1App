from __future__ import annotations

import io
import uuid
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from app.core.config import get_settings


class AssetService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.storage_backend = self.settings.asset_storage_backend.lower().strip()
        self.local_base_dir: Path = self.settings.assets_dir
        self.local_url_prefix = self.settings.assets_local_url_prefix.rstrip('/')
        self._s3_client: Any | None = None

        if self.storage_backend not in {'local', 's3'}:
            raise ValueError('ASSET_STORAGE_BACKEND must be "local" or "s3"')

        if self.storage_backend == 'local':
            self.local_base_dir.mkdir(parents=True, exist_ok=True)
            return

        if not self.settings.s3_bucket_name:
            raise ValueError('S3_BUCKET_NAME is required when ASSET_STORAGE_BACKEND=s3')
        if not self.settings.assets_public_base_url:
            raise ValueError('ASSETS_PUBLIC_BASE_URL is required when ASSET_STORAGE_BACKEND=s3')

    def _get_s3_client(self) -> Any:
        if self._s3_client is not None:
            return self._s3_client

        try:
            import boto3
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError('boto3 must be installed for ASSET_STORAGE_BACKEND=s3') from exc

        session = boto3.session.Session(
            aws_access_key_id=self.settings.s3_access_key_id,
            aws_secret_access_key=self.settings.s3_secret_access_key,
            region_name=self.settings.s3_region_name,
        )

        self._s3_client = session.client(
            's3',
            endpoint_url=self.settings.s3_endpoint_url,
        )
        return self._s3_client

    def _public_url(self, key: str) -> str:
        base = (self.settings.assets_public_base_url or '').rstrip('/')
        return f'{base}/{key}'

    def _object_key(self, filename: str) -> str:
        prefix = (self.settings.s3_key_prefix or '').strip('/')
        return f'{prefix}/{filename}' if prefix else filename

    def save_figure(self, fig: plt.Figure, prefix: str) -> str:
        filename = f'{prefix}_{uuid.uuid4().hex[:12]}.png'

        if self.storage_backend == 'local':
            abs_path = self.local_base_dir / filename
            fig.savefig(abs_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            return f'{self.local_url_prefix}/{filename}'

        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)

        key = self._object_key(filename)
        client = self._get_s3_client()
        client.put_object(
            Bucket=self.settings.s3_bucket_name,
            Key=key,
            Body=buffer.getvalue(),
            ContentType='image/png',
            CacheControl='public, max-age=31536000, immutable',
        )
        return self._public_url(key)


asset_service = AssetService()
