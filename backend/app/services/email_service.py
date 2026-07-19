import logging
import smtplib
from email.mime.text import MIMEText

from app.core.config import get_settings

logger = logging.getLogger("campus_eats.email")


class EmailService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def send(self, to: str, subject: str, body: str) -> None:
        if not self.settings.smtp_host or not self.settings.smtp_user:
            logger.info("[console-email] to=%s subject=%s body=%s", to, subject, body)
            return

        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = self.settings.smtp_from
        message["To"] = to

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
            server.starttls()
            server.login(self.settings.smtp_user, self.settings.smtp_password)
            server.sendmail(self.settings.smtp_from, [to], message.as_string())
