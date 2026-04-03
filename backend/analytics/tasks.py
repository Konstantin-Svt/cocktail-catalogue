import pandas
import pyarrow
from celery import shared_task
from django.conf import settings
from google.api_core.exceptions import GoogleAPIError
from google.cloud import bigquery
from django.db import connection

from analytics.services import (
    create_page_view_event,
    create_filter_applied_events,
    create_card_view_events,
    create_cocktail_page_open_event,
    create_login_event,
    create_signup_event,
    create_logout_event,
)

ENGINE = connection
DATASET_ID = str(settings.ANALYTICS_DATASET_ID)

# Because the 'analytics_event' table contains many columns with NULL-able values
# (sometimes even without a single actual data record per frame chunk),
# pyarrow doesn't know how to automatically convert data types.
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


@shared_task(bind=True, retry_kwargs={"max_retries": 3})
def cocktail_list_analytics_wrapper(
    self, request_dict: dict, response_dict: dict
) -> None:
    analytic_session = create_page_view_event(request_dict, "search")
    create_filter_applied_events(request_dict, response_dict, analytic_session)
    create_card_view_events(
        request_dict, response_dict, "search_results", analytic_session
    )


@shared_task(bind=True, retry_kwargs={"max_retries": 3})
def cocktail_detail_analytics_wrapper(
    self, request_dict: dict, response_dict: dict
) -> None:
    analytic_session = create_page_view_event(request_dict, "cocktail_page")
    create_cocktail_page_open_event(
        request_dict, response_dict, analytic_session
    )
    create_card_view_events(
        request_dict, response_dict, "similar_cocktails", analytic_session
    )


@shared_task(bind=True, retry_kwargs={"max_retries": 3})
def login_analytics_wrapper(self, request_dict: dict) -> None:
    analytic_session = create_page_view_event(request_dict, "login")
    create_login_event(request_dict, analytic_session)


@shared_task(bind=True, retry_kwargs={"max_retries": 3})
def signup_analytics_wrapper(self, request_dict: dict) -> None:
    analytic_session = create_page_view_event(request_dict, "signup")
    create_signup_event(request_dict, analytic_session)


@shared_task(bind=True, retry_kwargs={"max_retries": 3})
def logout_analytics_wrapper(self, request_dict: dict) -> None:
    create_logout_event(request_dict)
