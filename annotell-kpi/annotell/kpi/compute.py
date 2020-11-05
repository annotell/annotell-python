from pyspark import SparkContext
from pyspark.sql import SQLContext


def setup_spark(app_name: str) -> (SparkContext, SQLContext):
    spark_context = SparkContext(appName=app_name)
    spark_sql_context = SQLContext(spark_context)
    return spark_context, spark_sql_context


def get_dataproc_job_id(conf):
    tags = str(conf.get("spark.yarn.tags")).split(',')
    for tag in tags:
        if 'dataproc_job_' in tag:
            return tag.split('dataproc_job_', 1)[1]


def get_emr_job_id(conf):
    return conf.get("spark.yarn.tags").split("-")[2]

