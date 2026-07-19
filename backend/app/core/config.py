from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "Campus Eats"
    environment: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # Security
    secret_key: str = Field(default="change-me-in-env")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]

    # Database
    database_url: str = "postgresql+asyncpg://campus_eats:campus_eats@localhost:5432/campus_eats"
    database_url_sync: str = "postgresql+psycopg2://campus_eats:campus_eats@localhost:5432/campus_eats"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Seed admin
    default_admin_email: str = "admin@campuseats.com"
    default_admin_password: str = "ChangeMe123!"
    default_admin_phone: str = "9999999999"

    # Razorpay (test mode)
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""

    # Google Maps
    google_maps_api_key: str = ""

    # Cloudinary
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # SMTP (email notifications)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "no-reply@campuseats.local"

    # Notification provider: "console" (dev/log stub) or "twilio" etc later
    sms_provider: str = "console"
    whatsapp_provider: str = "console"

    # Order pricing defaults (in smallest currency unit-free decimal, INR)
    delivery_charge: float = 15.0
    packing_charge: float = 5.0
    gst_percent: float = 5.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
