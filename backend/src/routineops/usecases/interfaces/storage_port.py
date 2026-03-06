from abc import ABC, abstractmethod


class StoragePort(ABC):
    @abstractmethod
    def generate_upload_url(
        self, key: str, content_type: str, expires_in: int = 3600
    ) -> str:
        """Generate a pre-signed URL for uploading an object."""
        ...

    @abstractmethod
    def generate_download_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a pre-signed URL for downloading an object."""
        ...

    @abstractmethod
    def delete_object(self, key: str) -> None:
        """Delete an object from storage."""
        ...
