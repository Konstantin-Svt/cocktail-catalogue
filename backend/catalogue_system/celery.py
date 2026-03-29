import os

from celery import Celery
from rest_framework.request import Request

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "catalogue_system.settings")

app = Celery("catalogue_system")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))


def request_dict_converter(request: Request) -> dict:
    request_dict = dict()
    request_dict["anon_id"] = request.anon_id
    request_dict["User-Agent"] = request.headers.get("User-Agent", "")
    request_dict["page_url"] = request.build_absolute_uri()
    request_dict["cocktail_page_id"] = (
        request.resolver_match.kwargs.get("pk")
        if request.resolver_match
        else None
    )
    request_dict["query_params"] = {
        key: ",".join(value) for key, value in request.query_params.lists()
    }
    return request_dict


def response_data_dict_converter(response_data: dict) -> dict:
    safe_data = dict()
    safe_data["id"] = response_data.get("id")
    safe_data["results"] = [
        {"id": result["id"]}
        for result in response_data.get("results")
        or response_data.get("similar_cocktails", [])
    ]
    return safe_data
