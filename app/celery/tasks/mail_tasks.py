from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import asyncio

from app.core.configs.config import settings
from app.celery.celery_config import celery_app


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
)


async def _send_mail_async(message, fm):
    await fm.send_message(message)


@celery_app.task
def user_mail_event(token: str, recipients: list[EmailStr]):
    try:
        verify_link = f"https://{settings.DOMEN}:8080/api/verify?token={token}"
        subject = "Подтвердите ваш email"
        body_text = f"Для подтверждения перейдите по ссылке: {verify_link}"

        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body_text,
            subtype="plain"
        )

        fm = FastMail(conf)
        # loop = asyncio.get_event_loop()
        # loop.create_task(_send_mail_async(message, fm))

        asyncio.run(fm.send_message(message))

        return {"mes": "ok"}
    except Exception:
        return {"mes": "err"}
