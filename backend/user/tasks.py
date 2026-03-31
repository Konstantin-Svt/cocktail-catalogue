from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import signing

from user.services import create_email_payload, send_email_via_provider


@shared_task(bind=True)
def send_verification_email(self, user_id) -> int:
    user = get_user_model().objects.get(pk=user_id)
    if settings.AUTO_VERIFY_EMAIL:
        user.email_verified = True
        return 299

    uid = signing.dumps(user_id, salt="email-confirmation-id")
    token = default_token_generator.make_token(user)
    link = f"{settings.FRONTEND_BASE_URL}/api/user/verify-email/?uid={uid}&token={token}"
    payload = create_email_payload(user.email, link, mail_type="verify")
    response = send_email_via_provider(payload)
    response.raise_for_status()
    return response.status_code
