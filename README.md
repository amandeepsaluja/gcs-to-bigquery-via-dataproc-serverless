# GCS to Bigquery via Dataproc Serverless Spark

In the project, we will use Dataproc Serverless to process data from GCS and write to Bigquery. We will be using a Google provided [Cloud Storage to BigQuery template](https://cloud.google.com/dataproc-serverless/docs/templates/storage-to-bigquery) to create a Dataproc Serverless job. The template is a Spark job that reads data from Cloud Storage and writes it to BigQuery. The template is a good starting point for creating your own Dataproc Serverless jobs.

As documentation mentions, this template only supports avro, parquet, csv, or json file format. What we are trying to do in this project is to process an Excel file. So we will need to convert the Excel file to csv file first. We will use [Cloud Functions](https://cloud.google.com/functions) to convert the Excel file to csv file and upload to GCS. Then we will use the template to process the csv file and write to Bigquery.

## Reference

- Google Cloud Platform
  - Dataproc
    - https://cloud.google.com/dataproc-serverless/docs/templates/storage-to-bigquery
    - https://cloud.google.com/dataproc-serverless/docs/overview
    - https://cloud.google.com/dataproc-serverless/docs/reference/rest/v1/projects.locations.batches/create
    - https://cloud.google.com/dataproc-serverless/docs/concepts/versions/dataproc-serverless-versions
      https://cloud.google.com/dataproc-serverless/docs/concepts/versions/spark-runtime-versions
  - Cloud Functions
    - https://cloud.google.com/functions/docs/writing/write-http-functions
- Terraform
  - https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/dataproc_job
  - https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloudfunctions2_function
- GitHub
  - https://github.com/GoogleCloudPlatform/dataproc-templates/tree/main/java/src/main/java/com/google/cloud/dataproc/templates/gcs#1-gcs-to-bigquery
  - https://github.com/GoogleCloudPlatform/dataproc-templates/tree/main/python
  - https://github.com/GoogleCloudPlatform/dataproc-templates/blob/main/notebooks/README.md
  - https://github.com/GoogleCloudPlatform/serverless-spark-workshop
