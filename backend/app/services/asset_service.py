from __future__ import annotations

import io
import logging
import uuid
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AssetService:
    def __init__(self) -> None:
        self.settings = get_settings()
        requested_backend = self.settings.asset_storage_backend.lower().strip()
        self.local_base_dir: Path = self.settings.assets_dir
        self.local_url_prefix = self.settings.assets_local_url_prefix.rstrip('/')
        self._s3_client: Any | None = None

        if requested_backend not in {'local', 's3'}:
            logger.warning('Unknown ASSET_STORAGE_BACKEND=%s. Falling back to local.', requested_backend)
            self.storage_backend = 'local'
        elif requested_backend == 's3' and (
            not self.settings.s3_bucket_name or not self.settings.assets_public_base_url
        ):
            logger.warning(
                'S3 backend selected but missing S3_BUCKET_NAME or ASSETS_PUBLIC_BASE_URL. Falling back to local.'
            )
            self.storage_backend = 'local'
        else:
            self.storage_backend = requested_backend

        self.local_base_dir.mkdir(parents=True, exist_ok=True)

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

        try:
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
        except Exception as exc:
            logger.warning('S3 upload failed, storing asset locally instead: %s', exc)
            abs_path = self.local_base_dir / filename
            fig.savefig(abs_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            return f'{self.local_url_prefix}/{filename}'


asset_service = AssetService()
