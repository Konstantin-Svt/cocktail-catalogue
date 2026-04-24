import json
import operator
from collections import defaultdict
from datetime import datetime, timedelta
from functools import reduce

import pandas
import pyarrow
import redis
from celery import shared_task
from django.conf import settings
from django.db.models import Window, F
from django.db.models.functions import RowNumber
from django.utils import timezone
from google.api_core.exceptions import GoogleAPIError
from google.cloud import bigquery
from django.db import connection
from user_agents import parse

from analytics.models import Session, Event

r = redis.from_url(settings.REDIS_URL)
ANALYTICS_BUFFER_SIZE = 30

ENGINE = connection
DATASET_ID = str(settings.ANALYTICS_DATASET_ID)

# Because the 'analytics_event' table contains many columns with NULL-able values
# (sometimes even without a single actual data record per frame chunk),
# pyarrow doesn't know how to automatically convert these data types.
# So for this table forced schema is used.
EVENT_DTYPE_SCHEMA = {
    "id": pandas.ArrowDtype(pyarrow.int64()),
    "event_name": pandas.ArrowDtype(pyarrow.string()),
    "timestamp": pandas.ArrowDtype(
        pyarrow.timestamp(
            "us", settings.TIME_ZONE if settings.USE_TZ else None
        )
    ),
    "anonymous_user_id": pandas.ArrowDtype(pyarrow.string()),
    "page_name": pandas.ArrowDtype(pyarrow.string()),
    "search_text": pandas.ArrowDtype(pyarrow.string()),
    "filter_type": pandas.ArrowDtype(pyarrow.string()),
    "filter_value": pandas.ArrowDtype(pyarrow.string()),
    "results_count": pandas.ArrowDtype(pyarrow.int64()),
    "servings_number": pandas.ArrowDtype(pyarrow.int64()),
    "age_confirmed": pandas.ArrowDtype(pyarrow.bool_()),
    "position": pandas.ArrowDtype(pyarrow.int64()),
    "cocktail_id": pandas.ArrowDtype(pyarrow.int64()),
    "session_id": pandas.ArrowDtype(pyarrow.int64()),
    "page_url": pandas.ArrowDtype(pyarrow.string()),
    "previous_filters": pandas.ArrowDtype(pyarrow.string()),
    "filters_applied": pandas.ArrowDtype(pyarrow.bool_()),
    "rating_value": pandas.ArrowDtype(pyarrow.int64()),
    "review_length": pandas.ArrowDtype(pyarrow.int64()),
    "source": pandas.ArrowDtype(pyarrow.string()),
    "success": pandas.ArrowDtype(pyarrow.bool_()),
    "user_id": pandas.ArrowDtype(pyarrow.int64()),
}


def clear_analytics_table(analytics_table: str) -> None:
    if "analytics" in analytics_table:
        with ENGINE.cursor() as cursor:
            cursor.execute(f"DELETE FROM public.{analytics_table}")


@shared_task(
    bind=True, retry_kwargs={"max_retries": 3}, autoretry_for=(GoogleAPIError,)
)
def migrate_data_to_bigquery(self) -> None:
    client = bigquery.Client()
    for appname in settings.APPS_WITH_ANALYTICS:
        tables = pandas.read_sql(
            f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            AND table_name LIKE '{appname}%%'
            """,
            ENGINE,
        )

        for table in tables["table_name"]:
            bq_table = table.removeprefix(f"{appname}_")
            if appname != "analytics":
                client.delete_table(
                    f"{DATASET_ID}.{bq_table}", not_found_ok=True
                )

            dtype = None
            if table == "analytics_event":
                dtype = EVENT_DTYPE_SCHEMA

            df_iter = pandas.read_sql(
                f"SELECT * FROM public.{table}",
                ENGINE,
                chunksize=10000,
                dtype=dtype,
            )

            print(f"Uploading {table}")
            for chunk in df_iter:
                client.load_table_from_dataframe(
                    chunk,
                    f"{DATASET_ID}.{bq_table}",
                    job_config=bigquery.LoadJobConfig(
                        write_disposition=(
                            bigquery.WriteDisposition.WRITE_APPEND
                        ),
                        schema_update_options=(
                            bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
                        ),
                    ),
                ).result()

            if appname == "analytics":
                clear_analytics_table(table)


@shared_task(retry_kwargs={"max_retries": 3})
def flush_events() -> str | None:
    events_map = defaultdict(list)
    db_sessions_map = dict()
    all_sessions = []
    min_time = timezone.now() - timedelta(minutes=30)
    lock = r.lock("flush_events_lock", timeout=30)

    if not lock.acquire(blocking=False):
        return None

    try:
        repop_counter = 0
        while True:
            item = r.rpoplpush("processing_buffer", "analytics_buffer")
            if not item:
                break
            repop_counter += 1

        pipe = r.pipeline()

        counter = ANALYTICS_BUFFER_SIZE + 10 + repop_counter
        for _ in range(counter):
            pipe.rpoplpush("analytics_buffer", "processing_buffer")
        for event in pipe.execute():
            if event:
                event = json.loads(event)
                event["timestamp"] = datetime.fromisoformat(event["timestamp"])
                min_time = min(
                    min_time, event["timestamp"] - timedelta(minutes=30)
                )
                events_map[event["anonymous_user_id"]].append(event)

        if not events_map:
            return None

        for session in list(
            Session.objects.filter(
                anonymous_user_id__in=events_map, session_end__gte=min_time
            )
            .annotate(
                rn=Window(
                    expression=RowNumber(),
                    partition_by=F("anonymous_user_id"),
                    order_by=(F("anonymous_user_id"), "-session_end"),
                )
            )
            .filter(rn=1)
        ):
            db_sessions_map[session.anonymous_user_id] = session

        for anon_id in events_map:
            events_map[anon_id].sort(key=lambda x: x["timestamp"])
            events = events_map[anon_id]
            curr_session = db_sessions_map.get(anon_id)
            parsed_ua = None
            for i, event in enumerate(events):
                ua = event.pop("User-Agent")
                event = Event(**event)
                events[i] = event
                if not parsed_ua:
                    parsed_ua = parse(ua)
                if not curr_session:
                    curr_session = Session(
                        anonymous_user_id=anon_id,
                        session_start=event.timestamp,
                        session_end=event.timestamp,
                        browser=parsed_ua.browser.family,
                        device_type=parsed_ua.os.family,
                        user_id=event.user_id,
                    )
                elif curr_session.session_end < event.timestamp - timedelta(
                    minutes=30
                ):
                    all_sessions.append(curr_session)
                    curr_session = Session(
                        anonymous_user_id=anon_id,
                        session_start=event.timestamp,
                        session_end=event.timestamp,
                        browser=parsed_ua.browser.family,
                        device_type=parsed_ua.os.family,
                        user_id=event.user_id,
                    )
                else:
                    curr_session.session_end = event.timestamp
                event.session = curr_session

            all_sessions.append(curr_session)

        Session.objects.bulk_create(
            all_sessions,
            update_conflicts=True,
            update_fields=["session_end"],
            unique_fields=["id"],
            batch_size=500,
        )
        Event.objects.bulk_create(
            ev := reduce(operator.add, events_map.values(), []), batch_size=500
        )
        r.ltrim("processing_buffer", counter, -1)
    finally:
        lock.release()

    return f"{len(ev)} events saved to the database."


@shared_task(retry_kwargs={"max_retries": 3})
def collect_events(events: list) -> str:
    pipe = r.pipeline()
    for event in events:
        pipe.rpush("analytics_buffer", json.dumps(event, default=str))
    pipe.execute()

    if r.llen("analytics_buffer") > ANALYTICS_BUFFER_SIZE:
        flush_events.delay()

    return f"{len(events)} event(s) pushed to the buffer."
