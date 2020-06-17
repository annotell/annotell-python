from uuid import uuid4

import pandas as pd

from pyspark.sql.dataframe import DataFrame
from pyspark.sql import SQLContext
from pyspark.sql import utils as sql_utils
from pyspark.sql.functions import col

from annotell.kpi import conf
from annotell.kpi.events import EventManager
from annotell.kpi.logging import get_logger

log = get_logger()


def internal_data_loader(absolute_data_path: str,
                         data_path: str,
                         compute_placement: str,
                         filter_dict: dict,
                         spark_sql_context: SQLContext,
                         partitions: int,
                         event_manager: EventManager):
    log.debug(f"absolute_data_path={absolute_data_path}")
    data_frame = load_parquet_files(spark_sql_context, compute_placement,
                                    absolute_data_path, data_path,
                                    partitions,
                                    event_manager)
    event_manager.submit(event_type=event_manager.EVENT_DATA_LOADED, context=f"/{data_path}")
    num_partitions = data_frame.rdd.getNumPartitions()
    event_manager.submit(event_type=event_manager.EVENT_DATA_LOADED, context=f"num_partitions={num_partitions}")
    filtered_data_frame = filter_data_frame(filter_dict, data_frame, event_manager)
    return filtered_data_frame


def filter_data_frame(filter_dict, data_frame, event_manager):
    if filter_dict:
        column_filters = filter_dict['content']['column_filters']
        # Currently we only support column filters with value matching
        for column_filter in column_filters:
            try:
                log.debug(f"filtered column={column_filter['column']} to match values={column_filter['values']}")
                data_frame = data_frame.filter(col(column_filter['column']).isin(column_filter['values']))
                event_manager.submit(event_type=event_manager.EVENT_DATA_FILTERED,
                                     context=f"column={column_filter['column']} "
                                             f"limited to values={column_filter['values']}")
            except sql_utils.AnalysisException:
                log.error(f"column {column_filter['column']} not found in DataFrame")
        return data_frame
    else:
        return data_frame


def load_parquet_files(spark_sql_context: SQLContext,
                       compute_placement: str,
                       absolute_data_path: str,
                       data_path: str,
                       partitions: int,
                       event_manager: EventManager):
    log.debug(f"compute_placement={compute_placement}")
    if compute_placement == conf.GOOGLE_CLOUD_DATAPROC:
        absolute_data_path = 'gs://annotell-kpi-manager/' + data_path
    if compute_placement == conf.AMAZON_SPARK_EMR:
        absolute_data_path = 's3://annotell-kpi-manager/' + data_path
    try:
        if partitions:
            return spark_sql_context.read.parquet(absolute_data_path).repartition(partitions)
        else:
            return spark_sql_context.read.parquet(absolute_data_path)
    except sql_utils.AnalysisException:
        event_manager.submit(event_type=event_manager.EVENT_DATA_LOADING_FAILED,
                             context=f"data_path={absolute_data_path} did not exist")
        raise Exception(f"data_path={absolute_data_path} did not exist")
