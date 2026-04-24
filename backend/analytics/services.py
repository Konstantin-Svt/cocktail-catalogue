from django.utils import timezone
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer

from analytics.tasks import collect_events


def create_event_from_frontend(
    serializer: ModelSerializer, request: Request
) -> dict:
    data = serializer.data
    data["user_id"] = (
        request.user.id if request.user.is_authenticated else None
    )
    data["anonymous_user_id"] = getattr(request, "anon_id", None)
    data["User-Agent"] = request.headers.get("User-Agent", "")
    data["timestamp"] = timezone.now()
    return data


def create_page_view_event(request: Request, page_name: str, user_id : int = None) -> dict:
    data = {
        "event_name": "page_view",
        "page_url": request.build_absolute_uri(),
        "User-Agent": request.headers.get("User-Agent", ""),
        "user_id": request.user.id if request.user.is_authenticated else user_id,
        "anonymous_user_id": getattr(request, "anon_id", None),
        "timestamp": timezone.now(),
    }
    q_params = request.query_params.copy()
    for key, value in request.query_params.items():
        if (
            (key == "max_price" and value == "180")
            or (key == "min_price" and value == "0")
            or key in ("page_size", "page")
        ):
            q_params.pop(key)

    if page_name == "search" and len(q_params) == 0:
        page_name = "home"
    elif page_name == "cocktail_page":
        data["cocktail_id"] = (
            request.resolver_match.kwargs.get("pk")
            if request.resolver_match
            else None
        )

    data["page_name"] = page_name

    return data


def create_filter_applied_events(request: Request, response: dict) -> list:
    user_id = request.user.id if request.user.is_authenticated else None
    user_agent = request.headers.get("User-Agent", "")
    now = timezone.now()
    anon_id = getattr(request, "anon_id", None)
    search = None
    q_params = request.query_params.copy()
    for key, value in request.query_params.items():
        if (
            (key == "max_price" and value == "180")
            or (key == "min_price" and value == "0")
            or key in ("page_size", "page")
        ):
            q_params.pop(key)
        if key == "search":
            search = value
            q_params.pop(key)

    result_count = len(response.get("results") or [])
    data_results = []

    if search is not None:
        data = {
            "event_name": "search_query",
            "search_text": search,
            "results_count": result_count,
            "filters_applied": True if len(q_params) > 0 else False,
            "User-Agent": user_agent,
            "user_id": user_id,
            "anonymous_user_id": anon_id,
            "timestamp": now,
        }
        data_results.append(data)

    for key, value in q_params.items():
        split_value = value.split(",")
        for v in split_value:
            data_results.append(
                {
                    "event_name": "filter_applied",
                    "filter_type": key,
                    "filter_value": v,
                    "results_count": result_count,
                    "User-Agent": user_agent,
                    "user_id": user_id,
                    "anonymous_user_id": anon_id,
                    "timestamp": now,
                }
            )

    return data_results


def create_card_view_events(
    request: Request, response: dict, source: str
) -> list:
    user_id = request.user.id if request.user.is_authenticated else None
    user_agent = request.headers.get("User-Agent", "")
    now = timezone.now()
    results = (
        response.get("results") or response.get("similar_cocktails") or []
    )
    anon_id = getattr(request, "anon_id", None)
    result_data = [
        {
            "event_name": "cocktail_card_view",
            "position": i,
            "cocktail_id": cocktail["id"],
            "source": source,
            "User-Agent": user_agent,
            "user_id": user_id,
            "anonymous_user_id": anon_id,
            "timestamp": now,
        }
        for i, cocktail in enumerate(results, start=1)
    ]

    return result_data


def create_cocktail_page_open_event(request: Request, response: dict) -> dict:
    data = {
        "event_name": "cocktail_page_open",
        "cocktail_id": response["id"],
        "User-Agent": request.headers.get("User-Agent", ""),
        "user_id": request.user.id if request.user.is_authenticated else None,
        "anonymous_user_id": getattr(request, "anon_id", None),
        "timestamp": timezone.now(),
    }
    return data


def create_signup_event(request: Request, user_id: int = None) -> dict:
    data = {
        "event_name": "signup",
        "success": True if user_id else False,
        "User-Agent": request.headers.get("User-Agent", ""),
        "user_id": user_id,
        "anonymous_user_id": getattr(request, "anon_id", None),
        "timestamp": timezone.now(),
    }
    return data


def create_login_event(request: Request, user_id: int = None) -> dict:
    data = {
        "event_name": "login",
        "success": True if user_id else False,
        "User-Agent": request.headers.get("User-Agent", ""),
        "user_id": user_id,
        "anonymous_user_id": getattr(request, "anon_id", None),
        "timestamp": timezone.now(),
    }
    return data


def create_logout_event(request: Request) -> dict:
    data = {
        "event_name": "logout",
        "success": True if request.user.is_authenticated else False,
        "User-Agent": request.headers.get("User-Agent", ""),
        "user_id": request.user.id if request.user.is_authenticated else None,
        "anonymous_user_id": getattr(request, "anon_id", None),
        "timestamp": timezone.now(),
    }
    return data


def cocktail_list_analytics_wrapper(request: Request, response: dict) -> None:
    events = (
        [create_page_view_event(request, "search")]
        + create_filter_applied_events(request, response)
        + create_card_view_events(request, response, "search_results")
    )
    collect_events.delay(events)


def cocktail_detail_analytics_wrapper(
    request: Request, response: dict
) -> None:
    events = [
        create_page_view_event(request, "cocktail_page"),
        create_cocktail_page_open_event(request, response),
    ] + create_card_view_events(request, response, "similar_cocktails")
    collect_events.delay(events)


def login_analytics_wrapper(request: Request, user_id: int = None) -> None:
    events = [
        create_page_view_event(request, "login", user_id),
        create_login_event(request, user_id),
    ]
    collect_events.delay(events)


def signup_analytics_wrapper(request: Request, user_id: int = None) -> None:
    events = [
        create_page_view_event(request, "signup", user_id),
        create_signup_event(request, user_id),
    ]
    collect_events.delay(events)


def logout_analytics_wrapper(request: Request) -> None:
    events = [create_logout_event(request)]
    collect_events.delay(events)
