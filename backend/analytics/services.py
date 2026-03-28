from datetime import timedelta
from typing import Iterable

from django.utils import timezone
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer
from user_agents import parse

from analytics.models import Session, Event
from catalogue_system.celery import request_dict_converter


def event_create_executor(
    data: dict | Iterable[Event],
    request_dict: dict,
    session: Session = None,
    bulk: bool = False,
) -> Session:
    """
    Creates analytics Event(s) and returns
    Session instance to which Event(s) were bound.
    """
    anon_id = request_dict["anon_id"]
    now = timezone.now()
    old_session = False if session else True

    if not session:
        session = (
            Session.objects.filter(
                anonymous_user_id=anon_id,
                session_end__gte=now - timedelta(minutes=30),
            )
            .order_by("-session_end")
            .first()
        )
    if not session:
        ua = parse(request_dict["User-Agent"])
        session = Session.objects.create(
            anonymous_user_id=anon_id,
            session_start=now,
            session_end=now,
            browser=ua.browser.family,
            device_type=ua.os.family,
        )
        old_session = False

    if bulk:
        for event in data:
            event.session_id = session.id
            event.anonymous_user_id = anon_id
            event.timestamp = now
        Event.objects.bulk_create(data)
    else:
        Event.objects.create(
            anonymous_user_id=anon_id, session=session, timestamp=now, **data
        )

    if old_session:
        session.session_end = now
        session.save(update_fields=["session_end"])

    return session


def create_event_from_frontend(
    serializer: ModelSerializer, request: Request
) -> Session:
    request_dict = request_dict_converter(request)
    data = serializer.data
    return event_create_executor(data, request_dict)


def create_page_view_event(
    request_dict: dict, page_name: str, session: Session = None
) -> Session:
    q_params = request_dict["query_params"].copy()
    data = {
        "event_name": "page_view",
        "page_url": request_dict["page_url"],
    }
    for key, value in request_dict["query_params"].items():
        if (
            (key == "max_price" and value == "180")
            or (key == "min_price" and value == "0")
            or key in ("page_size", "page")
        ):
            q_params.pop(key)

    if page_name == "search" and len(q_params) == 0:
        page_name = "home"
    elif page_name == "cocktail_page":
        data["cocktail_id"] = request_dict["cocktail_page_id"]

    data["page_name"] = page_name

    session = event_create_executor(data, request_dict, session)
    return session


def create_filter_applied_events(
    request_dict: dict, response_dict: dict, session: Session = None
) -> Session:
    search = None
    q_params = request_dict["query_params"].copy()
    for key, value in request_dict["query_params"].items():
        if (
            (key == "max_price" and value == "180")
            or (key == "min_price" and value == "0")
            or key in ("page_size", "page")
        ):
            q_params.pop(key)
        if key == "search":
            search = value
            q_params.pop(key)

    result_count = len(response_dict["results"])
    if search is not None:
        data = {
            "event_name": "search_query",
            "search_text": search,
            "results_count": result_count,
            "filters_applied": True if len(q_params) > 0 else False,
        }
        session = event_create_executor(data, request_dict, session)

    bulk_data = []
    for key, value in q_params.items():
        split_value = value.split(",")
        for v in split_value:
            bulk_data.append(
                Event(
                    event_name="filter_applied",
                    filter_type=key,
                    filter_value=v,
                    results_count=result_count,
                )
            )

    session = event_create_executor(
        bulk_data, request_dict, session, bulk=True
    )
    return session


def create_card_view_events(
    request_dict: dict, response_dict: dict, session: Session = None
) -> Session:
    results = response_dict["results"]
    bulk_data = [
        Event(
            event_name="cocktail_card_view",
            position=i,
            cocktail_id=cocktail["id"],
        )
        for i, cocktail in enumerate(results, start=1)
    ]

    session = event_create_executor(
        bulk_data, request_dict, session, bulk=True
    )
    return session


def create_cocktail_page_open_event(
    request_dict: dict, response_dict: dict, session: Session = None
) -> Session:
    data = {
        "event_name": "cocktail_page_open",
        "cocktail_id": response_dict["id"],
    }
    session = event_create_executor(data, request_dict, session)
    return session
