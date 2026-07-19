import secrets

from redis.asyncio import Redis

from app.services.notification_provider import NotificationProvider

OTP_TTL_SECONDS = 300
OTP_KEY_PREFIX = "otp:"


class OtpService:
    def __init__(self, redis: Redis, sms_provider: NotificationProvider):
        self.redis = redis
        self.sms_provider = sms_provider

    async def request_otp(self, phone: str) -> None:
        code = f"{secrets.randbelow(1_000_000):06d}"
        await self.redis.set(f"{OTP_KEY_PREFIX}{phone}", code, ex=OTP_TTL_SECONDS)
        await self.sms_provider.send(phone, f"Your Campus Eats OTP is {code}. Valid for 5 minutes.")

    async def verify_otp(self, phone: str, code: str) -> bool:
        key = f"{OTP_KEY_PREFIX}{phone}"
        stored = await self.redis.get(key)
        if stored is None or stored != code:
            return False
        await self.redis.delete(key)
        return True
