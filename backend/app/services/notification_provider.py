"""Pluggable notification providers.

Default is a console/log-based stub — no telephony account needed to run
the app locally. Swap `sms_provider`/`whatsapp_provider` in config for a
real backend (Twilio, MSG91, WhatsApp Business API) by adding a class here
and wiring it into the `get_sms_provider`/`get_whatsapp_provider` factories;
callers depend only on the `NotificationProvider` protocol below.
"""

import logging
from typing import Protocol

from app.core.config import get_settings

logger = logging.getLogger("campus_eats.notifications")


class NotificationProvider(Protocol):
    async def send(self, to: str, message: str) -> None: ...


class ConsoleNotificationProvider:
    """Logs the message instead of sending it — the default dev/test backend."""

    async def send(self, to: str, message: str) -> None:
        logger.info("[console-notification] to=%s message=%s", to, message)


def get_sms_provider() -> NotificationProvider:
    settings = get_settings()
    if settings.sms_provider == "console":
        return ConsoleNotificationProvider()
    raise NotImplementedError(f"SMS provider '{settings.sms_provider}' is not configured")


def get_whatsapp_provider() -> NotificationProvider:
    settings = get_settings()
    if settings.whatsapp_provider == "console":
        return ConsoleNotificationProvider()
    raise NotImplementedError(f"WhatsApp provider '{settings.whatsapp_provider}' is not configured")
