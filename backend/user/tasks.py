from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.db.models import Q, F
from django.utils import timezone

from user.authentication import EmailVerificationTokenGenerator
from user.services import create_email_payload, send_email_via_provider

email_token_generator = EmailVerificationTokenGenerator()


@shared_task(bind=True, retry_kwargs={"max_retries": 3})
def send_verification_email(self, user_id) -> int:
    if settings.AUTO_VERIFY_EMAIL:
        get_user_model().objects.filter(pk=user_id).update(email_verified=True)
        return 299

    updated = (
        get_user_model()
        .objects.filter(
            Q(pk=user_id)
            & Q(daily_mail_count__lt=settings.DAILY_MAIL_THRESHOLD)
            & (
                Q(last_mail_sent__isnull=True)
                | Q(last_mail_sent__lte=timezone.now() - timedelta(seconds=30))
            )
        )
        .update(
            last_mail_sent=timezone.now(),
            daily_mail_count=F("daily_mail_count") + 1,
        )
    )
    if not updated:
        return 0

    user = get_user_model().objects.get(pk=user_id)
    uid = signing.dumps(user_id, salt="email-confirmation-id")
    token = email_token_generator.make_token(user)
    link = f"{settings.FRONTEND_BASE_URL}/register-verify-email/?uid={uid}&token={token}"
    payload = create_email_payload(user.email, link, mail_type="email_verify")
    response = send_email_via_provider(payload)
    response.raise_for_status()
    return response.status_code


@shared_task(bind=True, retry_kwargs={"max_retries": 3})
def send_change_email(self, user_id, new_email) -> int:
    if settings.AUTO_VERIFY_EMAIL:
        existing_user = (
            get_user_model().objects.filter(email=new_email).first()
        )
        if existing_user:
            if existing_user.email_verified is True:
                return 400
            existing_user.delete()
        get_user_model().objects.filter(pk=user_id).update(email=new_email)
        return 299

    updated = (
        get_user_model()
        .objects.filter(
            Q(pk=user_id)
            & Q(daily_mail_count__lt=settings.DAILY_MAIL_THRESHOLD)
            & (
                Q(last_mail_sent__isnull=True)
                | Q(last_mail_sent__lte=timezone.now() - timedelta(seconds=30))
            )
        )
        .update(
            last_mail_sent=timezone.now(),
            daily_mail_count=F("daily_mail_count") + 1,
        )
    )
    if not updated:
        return 0

    user = get_user_model().objects.get(pk=user_id)
    payload_old = create_email_payload(
        user.email, mail_type="email_change_warn"
    )
    send_email_via_provider(payload_old)

    uid = signing.dumps([user_id, new_email], salt="email-change-id")
    token = email_token_generator.make_token(user)
    link = (
        f"{settings.FRONTEND_BASE_URL}/verify-email/?uid={uid}&token={token}"
    )
    payload = create_email_payload(new_email, link, mail_type="email_change")
    response = send_email_via_provider(payload)
    response.raise_for_status()
    return response.status_code


@shared_task(bind=True, retry_kwargs={"max_retries": 3})
def send_reset_password_email(self, user_id):
    user = get_user_model().objects.get(pk=user_id)
    uid = signing.dumps(user_id, salt="password-reset-id")
    token = default_token_generator.make_token(user)
    link = f"{settings.FRONTEND_BASE_URL}/restore/?uid={uid}&token={token}"
    if settings.AUTO_VERIFY_EMAIL:
        return link

    updated = (
        get_user_model()
        .objects.filter(
            Q(pk=user_id)
            & Q(daily_mail_count__lt=settings.DAILY_MAIL_THRESHOLD)
            & (
                Q(last_mail_sent__isnull=True)
                | Q(last_mail_sent__lte=timezone.now() - timedelta(seconds=30))
            )
        )
        .update(
            last_mail_sent=timezone.now(),
            daily_mail_count=F("daily_mail_count") + 1,
        )
    )
    if not updated:
        return 0

    payload = create_email_payload(
        user.email, link, mail_type="password_reset"
    )
    response = send_email_via_provider(payload)
    response.raise_for_status()
    return response.status_code
