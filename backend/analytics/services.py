from datetime import timedelta
from typing import Iterable

from django.db import transaction
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer
from user_agents import parse

from analytics.models import Session, Event


@transaction.atomic
def event_create_executor(
    data: dict, request: Request, bulk: bool = False
) -> Event | int:
    session = (
        Session.objects.filter(
            anonymous_user_id=request.anon_id,
            session_end__gte=timezone.now() - timedelta(minutes=30),
        )
        .order_by("-session_end")
        .select_for_update()
        .first()
    )
    data.pop("timestamp", None)
    if session:
        event = Event.objects.create(
            anonymous_user_id=request.anon_id, session=session, **data
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
        event = Event.objects.create(
            anonymous_user_id=request.anon_id,
            session=session,
            timestamp=session.session_end,
            **data
        )
    return event


def create_event_from_frontend(
    serializer: ModelSerializer, request: Request
) -> Event:
    data = serializer.data
    event = event_create_executor(data, request)
    return event


def create_page_view_event(page_name: str, request: Request) -> Event:
    data = {
        "event_name": "page_view",
        "page_url": request.build_absolute_uri()
    }
    if (
        page_name == "search"
        and set(request.query_params.keys())
        == {
            "max_price",
            "min_price",
            "page_size",
            "page",
        }
        and request.query_params.get("max_price") == "180"
        and request.query_params.get("min_price") == "0"
    ):
        page_name = "home"
    elif page_name == "cocktail_page":
        data["cocktail_id"] = request.resolver_match.kwargs["id"]

    data["page_name"] = page_name

    event = event_create_executor(data, request)
    return event
