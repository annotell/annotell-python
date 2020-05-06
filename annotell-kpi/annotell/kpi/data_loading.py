from annotell.kpi.events import EventManager
from annotell.kpi.logging import get_logger
from pyspark.sql import SQLContext
from pyspark.sql import utils as sql_utils
from pyspark.sql.functions import col

log = get_logger()


def internal_data_loader(absolute_data_path: str,
                         data_path: str,
                         compute_placement: str,
                         filter_dict: dict,
                         spark_sql_context: SQLContext,
                         event_manager: EventManager):
    log.debug(f"absolute_data_path={absolute_data_path}")
    log.info(f"data_path={data_path}")
    data_frame = load_parquet_files(spark_sql_context, compute_placement, absolute_data_path, data_path, event_manager)
    event_manager.submit(event_type=event_manager.EVENT_DATA_LOADED, context=f"data_path={absolute_data_path}")
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


def load_parquet_files(spark_sql_context: SQLContext, compute_placement: str, absolute_data_path: str, data_path: str,
                       event_manager: EventManager):
    log.info(f"loading data from {compute_placement}")
    if compute_placement == 'GOOGLE_CLOUD_DATAPROC':
        absolute_data_path = 'gs://annotell-kpi-manager/' + data_path
    try:
        return spark_sql_context.read.parquet(absolute_data_path)
    except sql_utils.AnalysisException:
        event_manager.submit(event_type=event_manager.EVENT_DATA_LOADING_FAILED,
                             context=f"data_path={absolute_data_path} did not exist")
        raise Exception(f"data_path={absolute_data_path} did not exist")
