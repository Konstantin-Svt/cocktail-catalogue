import pandas
from django.conf import settings
from google.cloud import bigquery
from sqlalchemy import create_engine


def migrate_data_to_bigquery():
    dataset_id = (
        f"{settings.ANALYTICS_DATASET_ID}"
    )
    client = bigquery.Client()
    database = settings.DATABASES["default"]
    engine = create_engine(
        f"postgresql://{database['USER']}:{database['PASSWORD']}"
        f"@{database['HOST']}:{database['PORT']}/{database['NAME']}",
    )
    for tablename in settings.APPS_WITH_ANALYTICS:
        tables = pandas.read_sql(
            f"""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname='public'
            AND tablename LIKE '{tablename}%%'
            """,
            engine,
        )
        for table in tables["tablename"]:
            df_iter = pandas.read_sql(
                f"SELECT * FROM public.{table}", engine, chunksize=10000
            )
            bq_table = table.removeprefix(f"{tablename}_")
            first_chunk = True
            print(f"Uploading {table}")
            for chunk in df_iter:
                client.load_table_from_dataframe(
                    chunk,
                    f"{dataset_id}.{bq_table}",
                    job_config=bigquery.LoadJobConfig(
                        write_disposition=(
                            bigquery.WriteDisposition.WRITE_TRUNCATE
                            if first_chunk is True
                            else bigquery.WriteDisposition.WRITE_APPEND
                        ),
                    ),
                ).result()
                first_chunk = False
