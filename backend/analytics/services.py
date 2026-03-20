from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer
from user_agents import parse

from analytics.models import Session


@transaction.atomic
def create_event_from_frontend(serializer: ModelSerializer, request: Request):
    session = (
        Session.objects.filter(
            anonymous_user_id=request.anon_id,
            session_end__gte=timezone.now() - timedelta(minutes=30),
        )
        .order_by("-session_end")
        .select_for_update()
        .first()
    )
    if session:
        event = serializer.save(
            anonymous_user_id=request.anon_id, session=session
        )
        session.session_end = event.timestamp
        session.save(update_fields=["session_end"])
    else:
        ua = parse(request.headers.get("User-Agent", ""))
        session = Session.objects.create(
            anonymous_user_id=request.anon_id,
            browser=ua.browser.family,
            device_type=ua.os.family,
        )
        event = serializer.save(
            anonymous_user_id=request.anon_id,
            session=session,
            timestamp=session.session_end,
        )
    return event
