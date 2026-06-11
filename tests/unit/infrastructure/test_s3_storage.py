"""Unit tests for S3StorageImpl presigned URL generation."""

import os
from unittest.mock import MagicMock, patch

import pytest

from routineops.config.settings import clear_settings_caches
from routineops.infrastructure.storage.s3_storage import S3StorageImpl


@pytest.fixture
def mock_s3_client():
    with patch("routineops.infrastructure.storage.s3_storage.boto3") as mock_boto3:
        client = MagicMock()
        mock_boto3.client.return_value = client
        yield client


class TestBucketResolution:
    def test_uses_explicit_bucket_name(self, mock_s3_client: MagicMock) -> None:
        storage = S3StorageImpl(bucket_name="explicit-bucket")
        storage.generate_download_url("some/key")

        params = mock_s3_client.generate_presigned_url.call_args.kwargs["Params"]
        assert params["Bucket"] == "explicit-bucket"

    def test_falls_back_to_settings_bucket(self, mock_s3_client: MagicMock) -> None:
        with patch.dict(os.environ, {"EVIDENCE_BUCKET_NAME": "settings-bucket"}, clear=False):
            clear_settings_caches()
            storage = S3StorageImpl()
        clear_settings_caches()

        storage.generate_download_url("some/key")
        params = mock_s3_client.generate_presigned_url.call_args.kwargs["Params"]
        assert params["Bucket"] == "settings-bucket"

    def test_raises_when_bucket_is_not_configured(self, mock_s3_client: MagicMock) -> None:
        env = {k: v for k, v in os.environ.items() if k != "EVIDENCE_BUCKET_NAME"}
        with patch.dict(os.environ, env, clear=True):
            clear_settings_caches()
            with pytest.raises(ValueError, match="EVIDENCE_BUCKET_NAME is not configured"):
                S3StorageImpl()
        clear_settings_caches()


class TestPresignedUrls:
    def test_generate_upload_url_builds_put_object_request(self, mock_s3_client: MagicMock) -> None:
        mock_s3_client.generate_presigned_url.return_value = "https://s3/upload"
        storage = S3StorageImpl(bucket_name="bucket")

        url = storage.generate_upload_url("evidence/key", "image/png")

        assert url == "https://s3/upload"
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            "put_object",
            Params={
                "Bucket": "bucket",
                "Key": "evidence/key",
                "ContentType": "image/png",
            },
            ExpiresIn=3600,
        )

    def test_generate_upload_url_honors_custom_expiry(self, mock_s3_client: MagicMock) -> None:
        storage = S3StorageImpl(bucket_name="bucket")

        storage.generate_upload_url("evidence/key", "image/jpeg", expires_in=60)

        assert mock_s3_client.generate_presigned_url.call_args.kwargs["ExpiresIn"] == 60

    def test_generate_download_url_builds_get_object_request(
        self, mock_s3_client: MagicMock
    ) -> None:
        mock_s3_client.generate_presigned_url.return_value = "https://s3/download"
        storage = S3StorageImpl(bucket_name="bucket")

        url = storage.generate_download_url("evidence/key")

        assert url == "https://s3/download"
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            "get_object",
            Params={"Bucket": "bucket", "Key": "evidence/key"},
            ExpiresIn=3600,
        )

    def test_delete_object_targets_bucket_and_key(self, mock_s3_client: MagicMock) -> None:
        storage = S3StorageImpl(bucket_name="bucket")

        storage.delete_object("evidence/key")

        mock_s3_client.delete_object.assert_called_once_with(Bucket="bucket", Key="evidence/key")
