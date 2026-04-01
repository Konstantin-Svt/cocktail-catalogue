from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing

from user.authentication import EmailVerificationTokenGenerator
from user.services import create_email_payload, send_email_via_provider

email_token_generator = EmailVerificationTokenGenerator()


@shared_task(bind=True)
def send_verification_email(self, user_id) -> int:
    user = get_user_model().objects.get(pk=user_id)
    if settings.AUTO_VERIFY_EMAIL:
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        return 299

    uid = signing.dumps(user_id, salt="email-confirmation-id")
    token = email_token_generator.make_token(user)
    link = f"{settings.FRONTEND_BASE_URL}/api/user/verify-email/?uid={uid}&token={token}"
    payload = create_email_payload(user.email, link, mail_type="verify")
    response = send_email_via_provider(payload)
    response.raise_for_status()
    return response.status_code
