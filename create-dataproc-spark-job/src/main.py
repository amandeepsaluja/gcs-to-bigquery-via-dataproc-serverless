import functions_framework
import yaml

# from googleapiclient.discovery import build


@functions_framework.cloud_event
def create_dataproc_spark_job(cloudevent):
    # Getting payload data from the Cloud Storage event
    payload = cloudevent.data.get("protoPayload")
    resource_name = payload.get("resourceName")

    # parsing configuration
    with open("config.yaml", "r") as yaml_file:
        config_data = yaml.load(yaml_file, Loader=yaml.FullLoader)

    # extracting full gcs path from resource name
    full_gcs_path = "gs://" + resource_name.split("/", maxsplit=3)[-1].replace(
        "/objects", ""
    )
    gcs_bucket_name = full_gcs_path.split("/", maxsplit=3)[2]
    excel_source = full_gcs_path.split("/", maxsplit=3)[-1]

    # specifying variables for triggering excel to csv cloud function
    source_excel_bucket = gcs_bucket_name
    source_excel_file = excel_source
    target_csv_bucket = gcs_bucket_name
    target_csv_file = excel_source.rsplit(".", maxsplit=1)[0] + ".csv"

    # triggering excel to csv cloud function
    function_url = config_data["EXCEL_TO_CSV_CLOUD_FUNCTION"]
    function_headers = {"Content-Type": "application/json"}
    function_data = {
        "source_excel_bucket": source_excel_bucket,
        "source_excel_file": source_excel_file,
        "target_csv_bucket": target_csv_bucket,
        "target_csv_file": target_csv_file,
    }
    response = functions_framework.post(
        function_url, headers=function_headers, json=function_data
    )

    return print(str(response))
