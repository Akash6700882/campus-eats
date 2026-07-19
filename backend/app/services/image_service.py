import cloudinary
import cloudinary.uploader

from app.core.config import get_settings


class ImageUploadError(Exception):
    pass


class ImageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        if self._configured:
            cloudinary.config(
                cloud_name=self.settings.cloudinary_cloud_name,
                api_key=self.settings.cloudinary_api_key,
                api_secret=self.settings.cloudinary_api_secret,
                secure=True,
            )

    @property
    def _configured(self) -> bool:
        return bool(
            self.settings.cloudinary_cloud_name
            and self.settings.cloudinary_api_key
            and self.settings.cloudinary_api_secret
        )

    def upload(self, file_bytes: bytes, folder: str) -> str:
        if not self._configured:
            raise ImageUploadError(
                "Cloudinary is not configured — set CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET in .env"
            )
        result = cloudinary.uploader.upload(file_bytes, folder=folder)
        return result["secure_url"]
