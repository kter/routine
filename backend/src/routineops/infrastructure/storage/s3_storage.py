import boto3

from routineops.config.settings import get_api_settings
from routineops.usecases.interfaces.storage_port import StoragePort


class S3StorageImpl(StoragePort):
    def __init__(self, bucket_name: str | None = None) -> None:
        resolved_bucket = bucket_name or get_api_settings().evidence_bucket_name
        if not resolved_bucket:
            raise ValueError("EVIDENCE_BUCKET_NAME is not configured")
        self._bucket = resolved_bucket
        self._client = boto3.client("s3")

    def generate_upload_url(self, key: str, content_type: str, expires_in: int = 3600) -> str:
        url: str = self._client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self._bucket,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )
        return url

    def generate_download_url(self, key: str, expires_in: int = 3600) -> str:
        url: str = self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return url

    def delete_object(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)
