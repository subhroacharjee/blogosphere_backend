import asyncio
from django.utils import timezone
from uuid import uuid4

from django.core.mail import send_mail
from django.utils.log import logging
from django.utils.timezone import timedelta
from users.models import User, VerifyToken

logger = logging.getLogger(__name__)


def create_token_and_send_verify_email(user: User):
    token = str(uuid4())
    new_token = VerifyToken(
        user=user,
        token=token,
        used_for="V",
        expires_at=timezone.now() + timedelta(hours=1),
    )
    new_token.save()
    asyncio.run(_send_verify_email_async_caller(token, user.email))
    pass


async def _send_verify_email_async_caller(token, email):
    asyncio.create_task(_send_verify_email_async(token, email))


async def _send_verify_email_async(token, email):
    send_mail(
        "Verify User",
        f"Please use this verification token to activate your account: {token}",
        "no-reply@mailtrap.io",
        [
            email,
        ],
        fail_silently=False,
    )
