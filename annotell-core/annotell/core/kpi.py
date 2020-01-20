from pyspark import SparkContext
from annotell.core.loader import parquet_loader


def create_spark_context(sessionName, remote='local'):
    return SparkContext(remote, sessionName)


def load_test_data(sparkContext):
    return parquet_loader.load_file(sparkContext=sparkContext, path='sample_data/sample.parquet')


def list_signals(dataFrame):
    dataFrame.printSchema()
