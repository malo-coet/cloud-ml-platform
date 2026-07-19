from functools import lru_cache
from typing import Annotated, BinaryIO

import boto3
from fastapi import Depends

from app.core.config import settings


class ObjectStorage:
    """Thin wrapper around the S3 API (MinIO locally)."""

    def __init__(
        self,
        endpoint_url: str,
        public_endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket: str,
    ) -> None:
        self.bucket = bucket
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        # Separate client for presigned URLs: they must be signed for the
        # hostname the *browser* will use, not the internal Docker hostname.
        self._public_client = boto3.client(
            "s3",
            endpoint_url=public_endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def upload(self, fileobj: BinaryIO, key: str, content_type: str | None = None) -> None:
        extra_args = {"ContentType": content_type} if content_type else None
        self._client.upload_fileobj(fileobj, self.bucket, key, ExtraArgs=extra_args)

    def delete(self, key: str) -> None:
        self._client.delete_object(Bucket=self.bucket, Key=key)

    def presigned_download_url(self, key: str, filename: str, expires_in: int = 900) -> str:
        return self._public_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket,
                "Key": key,
                "ResponseContentDisposition": f'attachment; filename="{filename}"',
            },
            ExpiresIn=expires_in,
        )


@lru_cache
def get_storage() -> ObjectStorage:
    return ObjectStorage(
        endpoint_url=settings.s3_endpoint_url,
        public_endpoint_url=settings.s3_public_endpoint_url,
        access_key=settings.aws_access_key_id,
        secret_key=settings.aws_secret_access_key,
        bucket=settings.s3_datasets_bucket,
    )


Storage = Annotated[ObjectStorage, Depends(get_storage)]
