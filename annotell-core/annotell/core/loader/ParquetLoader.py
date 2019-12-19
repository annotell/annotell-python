from pyspark import SparkContext, SQLContext

def load_file(sparkContext, path):
    sqlContext = SQLContext(sparkContext)
    return sqlContext.read.format("parquet").load(path)
