from pyspark import SparkContext, SQLContext


def load_file(spark_context, path):
    sql_context = SQLContext(spark_context)
    return sql_context.read.format("parquet").load(path)


def create_spark_context(session_name, remote='local'):
    return SparkContext(remote, session_name)
