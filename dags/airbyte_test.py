from airflow.hooks.S3_hook import S3Hook
from airflow.models import DAG, Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator

from python_extension.operators.python import ExtendedPythonOperator
from selenium_plugin.operators.selenium_operator import SeleniumOperator

from selenium_scripts.linkedin_download import scrape_linkedin

from datetime import timedelta, datetime

import os

import pendulum

# global variables
DAG_CONFIG = Variable.get("airbyte_config", deserialize_json=True)

# specify local timezone
local_tz = pendulum.timezone("Europe/London")

# DAG default args
default_args = {
    "owner": "niall_o_riordan",
    "start_date": datetime(2022, 4, 21, tzinfo=local_tz),
    "retries": 2,
    "retries_delay": timedelta(minutes=2),
}

dag = DAG(
    "airbyte_test",
    default_args=default_args,
    description="An Airflow DAG to test Airbyte",
    schedule_interval=timedelta(days=1),
    catchup=False,
)

with dag:

    # dummy task to specify start of dag
    start = DummyOperator(task_id="start")

    results_location = os.path.join(os.getenv("AIRFLOW_HOME"), "outputs", "linkedin.json")

    # selenium operator to download brandwatch data and preprocess
    scrape_linked_profiles = SeleniumOperator(
        selenium_address="airflow_selenium",
        script=scrape_linkedin,
        script_args=[
            "https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin",
            os.path.join(os.getenv("AIRFLOW_HOME"), "inputs", "profiles.csv"),
            results_location,
            "linkedin_access",
        ],
        task_id="scrape_linked_profiles",
    )

    def upload_file_to_S3(aws_conn_id: str, file_path: str, key: str, bucket_name: str):
        """
        Uploads a local file to s3.
        """
        import logging

        hook = S3Hook(aws_conn_id)
        hook.load_file(file_path, key, bucket_name, replace=True)
        logging.info(f"loaded {file_path} to s3 bucket:{bucket_name} as {key}")

    # Upload results to S3
    task_upload_to_s3 = ExtendedPythonOperator(
        task_id="upload_to_s3",
        python_callable=upload_file_to_S3,
        op_kwargs={
            "aws_conn_id": "aws_access",
            "file_path": results_location,
            "key": DAG_CONFIG["aws_s3_key"],
            "bucket_name": DAG_CONFIG["aws_s3_bucket"],
        },
    )

    # trigger Airbyte connector once results are uploaded to S3
    json_to_postgres = AirbyteTriggerSyncOperator(
        task_id="airbyte_airflow_linkedin",
        airbyte_conn_id="airbyte_linkedin_connection",
        connection_id="a0852e35-03f2-4040-8fac-b6d839d0751b",
        asynchronous=False,
        timeout=600,
        wait_seconds=10,
    )

    # dummy task to mark the end of the dag
    end = DummyOperator(task_id="end")


# set task dependencies
start >> scrape_linked_profiles >> task_upload_to_s3 >> json_to_postgres >> end
