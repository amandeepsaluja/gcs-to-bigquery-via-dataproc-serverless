import functions_framework
import google.oauth2.id_token
import json
import os
import re
import requests
import yaml

import google.auth.transport.requests as google_requests

from googleapiclient.discovery import build
from time import sleep


@functions_framework.cloud_event
def create_dataproc_spark_job(cloudevent):
    # Getting payload data from the Cloud Storage event
    payload = cloudevent.data.get("protoPayload")
    resource_name = payload.get("resourceName")

    # parsing configuration
    with open("config.yaml", "r") as yaml_file:
        config_data = yaml.load(yaml_file, Loader=yaml.FullLoader)

    audience = config_data["EXCEL_TO_CSV_CLOUD_FUNCTION"]

    # extracting full gcs path from resource name
    full_gcs_path = "gs://" + resource_name.split("/", maxsplit=3)[-1].replace(
        "/objects", ""
    )
    gcs_bucket_name = full_gcs_path.split("/", maxsplit=3)[2]
    excel_source = full_gcs_path.split("/", maxsplit=3)[-1]
    file_name = excel_source.split("/")[-1].split(".")[0]

    # specifying variables for triggering excel to csv cloud function
    source_excel_bucket = gcs_bucket_name
    source_excel_file = excel_source
    target_csv_bucket = gcs_bucket_name
    target_csv_file = excel_source.rsplit(".", maxsplit=1)[0] + ".csv"

    # authenticating for cloud function call
    request = google_requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(request, audience)

    # triggering excel to csv cloud function
    function_headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json",
    }
    function_data = {
        "source_excel_bucket": source_excel_bucket,
        "source_excel_file": source_excel_file,
        "target_csv_bucket": target_csv_bucket,
        "target_csv_file": target_csv_file,
    }

    response = requests.post(
        audience, headers=function_headers, data=json.dumps(function_data)
    )

    print("Waiting for 15 seconds for the excel to csv cloud function to complete")

    sleep(15)

    # creating dataproc spark job
    service = build("dataproc", "v1", cache_discovery=False)
    dataproc_job_request = (
        service.projects()
        .locations()
        .batches()
        .create(
            parent=f"projects/{config_data['PROJECT_ID']}/locations/{config_data['REGION']}",
            batchId=f"{re.sub(r'[^a-zA-Z0-9]+', '-', file_name)}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            body={
                "runtimeConfig": {"version": config_data["RUNTIME_VERSION"]},
                "environmentConfig": {
                    "executionConfig": {
                        "serviceAccount": os.environ.get(
                            "SERVICE_ACCOUNT_EMAIL"
                        )  # GitHub secret -> Terraform -> Cloud Function
                    }
                },
                "sparkBatch": {
                    "mainClass": config_data["SPARK_MAIN_CLASS"],
                    "args": [
                        "--template",
                        config_data["SPARK_TEMPLATE_NAME"],
                        "--templateProperty",
                        f"project.id={config_data['PROJECT_ID']}",
                        "--templateProperty",
                        f"gcs.bigquery.input.location={full_gcs_path}",
                        "--templateProperty",
                        "gcs.bigquery.input.format=csv",
                        "--templateProperty",
                        f"gcs.bigquery.output.dataset={config_data['BQ_DATASET']}",
                        "--templateProperty",
                        f"gcs.bigquery.output.table={config_data['BQ_TABLE']}",
                        "--templateProperty",
                        f"gcs.bigquery.temp.bucket.name={gcs_bucket_name}",
                    ],
                    "jarFileUris": config_data["SPARK_JAR_FILES"],
                },
            },
        )
    )

    response = dataproc_job_request.execute()

    return print(str(response))
