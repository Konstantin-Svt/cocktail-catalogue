import pandas
import pyarrow
from django.conf import settings
from google.cloud import bigquery
from django.db import connection

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
}
ENGINE = connection


def clear_analytics_table(analytics_table: str) -> None:
    with ENGINE.cursor() as cursor:
        cursor.execute(f"DELETE FROM public.{analytics_table}")


def migrate_data_to_bigquery() -> None:
    dataset_id = f"{settings.ANALYTICS_DATASET_ID}"
    client = bigquery.Client()
    for appname in settings.APPS_WITH_ANALYTICS:
        tables = pandas.read_sql(
            f"""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname='public'
            AND tablename LIKE '{appname}%%'
            """,
            ENGINE,
        )

        for table in tables["tablename"]:
            dtype = None
            if table == "analytics_event":
                dtype = EVENT_DTYPE_SCHEMA

            df_iter = pandas.read_sql(
                f"SELECT * FROM public.{table}",
                ENGINE,
                chunksize=10000,
                dtype=dtype,
            )

            first_chunk = True
            bq_table = table.removeprefix(f"{appname}_")
            print(f"Uploading {table}")

            for chunk in df_iter:
                client.load_table_from_dataframe(
                    chunk,
                    f"{dataset_id}.{bq_table}",
                    job_config=bigquery.LoadJobConfig(
                        write_disposition=(
                            bigquery.WriteDisposition.WRITE_TRUNCATE
                            if first_chunk and appname != "analytics"
                            else bigquery.WriteDisposition.WRITE_APPEND
                        ),
                        schema_update_options=[
                            bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
                        ],
                    ),
                ).result()
                first_chunk = False

            if appname == "analytics":
                clear_analytics_table(table)
