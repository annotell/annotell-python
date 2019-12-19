from pyspark import SparkContext, SQLContext
from annotell.core.loader import ParquetLoader
from annotell.core.datamodel import KpiDataTable


def create_spark_context(sessionName, remote='local'):
    return SparkContext(remote, sessionName)


def load_test_data(sparkContext) -> KpiDataTable:
    return ParquetLoader.load_file(sparkContext=sparkContext, path='sample_data/sample.parquet')


def list_signals(dataFrame):
    dataFrame.printSchema()
