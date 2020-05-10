import annotell.kpi.conf as conf

from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext


def setup_spark(app_name: str) -> (SparkContext, SQLContext):
    spark_config = SparkConf()
    spark_context = SparkContext(appName=app_name,
                                 master=conf.SPARK_MASTER,
                                 conf=spark_config)
    spark_context.setLogLevel(conf.SPARK_LOG_LEVEL)
    spark_sql_context = SQLContext(spark_context)
    return spark_context, spark_sql_context


def get_dataproc_job_id(conf):
    tags = str(conf.get("spark.yarn.tags")).split(',')
    for tag in tags:
        if 'dataproc_job_' in tag:
            return tag.split('dataproc_job_', 1)[1]
