import argparse
import atexit
import inspect
import json
import os
import uuid
from typing import BinaryIO

from annotell.kpi import conf
from annotell.kpi.events import EventManager
from annotell.kpi.files import FileManager
from annotell.kpi.logging import setup_logging
from annotell.kpi.results import ResultManager
from annotell.kpi.datasets import DatasetManager
from annotell.kpi.compute import setup_spark, get_dataproc_job_id, get_emr_job_id
from annotell.kpi.models import Result
from annotell.auth.authsession import AuthSession, DEFAULT_HOST as DEFAULT_AUTH_HOST

import annotell.kpi.storage as storage

from pyspark.sql.dataframe import DataFrame
from pyspark import SparkContext
from pyspark.sql import SQLContext
from typing import List

parser = argparse.ArgumentParser()
log = setup_logging()


class ExecutionManager:
    """The Execution Manager is necessary for running KPI scripts as part of the Annotell KPI Solution.

        By using the Execution Manager in a KPI script, the script is prepared to be submitted to the
        Annotell KPI Manager API. The KPI Manager will then execute the script, and the Execution Manager
        will take care of loading data, submitting results and other related activities.

        An example script should start with something like this

        ```
        from annotell.kpi.execution_manager import ExecutionManager
        execution_manager = ExecutionManager(project_id=1, dataset_id=1)
        data_frame, spark_context, spark_sql_context = execution_manager.load_data()
        ```
    """

    def __init__(self, project_id, dataset_id, kpi_host=conf.KPI_MANAGER_HOST, auth_host=DEFAULT_AUTH_HOST):
        parser.add_argument('--job-id', type=str, help='Job ID')
        parser.add_argument('--organization-id', type=str, help='Organization ID')
        parser.add_argument("--project-id", type=str, help="Enables overriding project_id via arguments")
        parser.add_argument("--dataset-id", type=str, help="Enables overriding dataset_id via arguments")
        parser.add_argument('--user-id', type=str, help='User ID')
        parser.add_argument("--filter-file", type=str, help="JSON filter from file")
        parser.add_argument("--filter-json", type=str, help="JSON string version of filter")
        parser.add_argument("--script-hash", type=str, help="Hash of file in current state")
        parser.add_argument("--client-id", type=str, help="Client ID used for authentication")
        parser.add_argument("--client-secret", type=str, help="Client secret used for authentication")
        parser.add_argument("--execution-mode", type=str, help="How is this script being run?")
        parser.add_argument("--compute-placement", type=str, help="Where will this workload be run?")

        args = parser.parse_args()

        # Here we put together information about the execution session. Since it should be possible to run scripts
        # both locally and in production, we use placeholders for variables that are only relevant
        # in production (such as organization_id).
        self.organization_id = args.organization_id or 'localhost'
        self.user_id = args.user_id or 'unknown'
        self.project_id = args.project_id or project_id  # first check overriding arguments
        self.dataset_id = args.dataset_id or dataset_id  # first check overriding arguments
        self.job_id = args.job_id or str(uuid.uuid4())  # Note that later overrides are possible
        self.script_hash = args.script_hash or 'local_execution_mode'
        self.execution_mode = args.execution_mode or 'local_execution_mode'
        self.kpi_host = kpi_host
        self.client_id = args.client_id or None
        self.client_secret = args.client_secret or None
        self.filter_file = args.filter_file or None
        self.filter_json = args.filter_json or None
        self.compute_placement = args.compute_placement or 'localhost'

        # To enable debugging in Spark clusters, we define the app_name based on the configuration
        self.app_name = 'project_id=' + str(self.project_id) + \
                        ':dataset_id=' + str(self.dataset_id)

        # Sets up Spark to run against a local master
        sc, sqlc = setup_spark(app_name=self.app_name)

        # If running in Google Cloud, replace job_id with ID from Yarn tags
        if self.compute_placement == 'GOOGLE_CLOUD_DATAPROC':
            self.job_id = get_dataproc_job_id(sc.getConf())
        if self.compute_placement == 'AMAZON_SPARK_EMR':
            self.job_id = get_emr_job_id(sc.getConf())
        log.info(f"[job_id              ] {self.job_id}")

        # Determine if credentials are to be used from arguments or environment variables
        if self.client_secret:
            log.info(f"[authentication      ] using submitted credentials")
            self.oauth_session = AuthSession(host=auth_host, client_id=self.client_id, client_secret=self.client_secret)
        else:
            log.info(f"[authentication      ] using environment credentials")
            self.oauth_session = AuthSession(host=auth_host)
        self.session = self.oauth_session.session

        # Parse potential filter to be used when loading data
        self.filter_dict, self.filter_id = self.parse_filter(filter_json=self.filter_json)

        # The Event Manager is used to send events used for script diagnostics
        self.event_manager = EventManager(
            auth_session=self.session, job_id=self.job_id, host=self.kpi_host, kpi_manager_version=conf.KPI_MANAGER_VERSION
        )

        # The Result Manager is used to send results to storage
        self.result_manager = ResultManager(
            auth_session=self.session,
            host=self.kpi_host,
            kpi_manager_version=conf.KPI_MANAGER_VERSION,
            execution_mode=self.execution_mode,
            script_hash=self.script_hash,
            job_id=self.job_id,
            project_id=self.project_id,
            dataset_id=self.dataset_id,
            filter_id=self.filter_id,
            event_manager=self.event_manager
        )

        self.file_manager = FileManager(
            auth_session=self.session,
            host=self.kpi_host,
            project_id=self.project_id,
            job_id=self.job_id,
            kpi_manager_version=conf.KPI_MANAGER_VERSION
        )

        # The Dataset manager is used to modify information about datasets
        self.dataset_manager = DatasetManager(
            auth_session=self.session, job_id=self.job_id, kpi_host=self.kpi_host, kpi_manager_version=conf.KPI_MANAGER_VERSION
        )

        # Data paths are defined by organization, project and dataset ids
        self.data_path = self.get_data_path(organization_id=self.organization_id, project_id=self.project_id, dataset_id=self.dataset_id)

        # Experimentation data paths are defined by organization and project
        # To facilitate experimentation we offer a way to load parquet files not associated with any specific dataset
        self.experimentation_data_path = self.get_experimentation_data_path(
            organization_id=self.organization_id, project_id=self.project_id
        )

        # When submitting the script via the KPI Manager we need to find the location of the script that started
        # the execution manager. To do this we inspect the execution stack.
        abs_path = os.path.abspath((inspect.stack()[1])[1])
        self.root_dir = os.path.dirname(abs_path)
        self.absolute_data_path = os.path.join(self.root_dir, self.data_path)

        self.spark_context = sc
        self.spark_sql_context = sqlc

        # Runs a function before the script finished
        atexit.register(self.event_manager.script_completed)

        # Submits an event to indicate the initialization completed successfully
        self.event_manager.script_initialized(
            organization_id=self.organization_id, project_id=self.project_id, dataset_id=self.dataset_id, user_id=self.user_id
        )

    def dataset_metadata_update_from_dict(self, metadata_dict: dict):
        for key in metadata_dict.keys():
            self.dataset_metadata_update(key=key, value=metadata_dict[key])

    def dataset_metadata_update(self, key, value):
        return self.dataset_manager.update_metadata(self.project_id, self.dataset_id, key, value)

    def dataset_metadata_get(self):
        dataset = self.dataset_manager.get_dataset(self.project_id, self.dataset_id)
        return dataset['dataset']['metadata']

    def submit_event(self, event_type: str, context: str):
        self.event_manager.submit(event_type=event_type, context=context)

    def load_data(self, partitions=None, merge_schema: bool = True) -> (DataFrame, SparkContext, SQLContext):
        """Loads data from either local disk or cloud infrastructure depending on Execution Mode.

        To enable both local development, and cloud based execution, of KPI scripts data loading is handled
        by the Execution Manager. The Execution Manager will be aware of the context in which it is running,
        and load data the appropriate way.
        """
        return storage.internal_data_loader(
            absolute_data_path=self.absolute_data_path,
            data_path=self.data_path,
            compute_placement=self.compute_placement,
            filter_dict=self.filter_dict,
            spark_sql_context=self.spark_sql_context,
            partitions=partitions,
            event_manager=self.event_manager,
            merge_schema=merge_schema), self.spark_context, self.spark_sql_context

    def load_experimentation_file(self, filename, merge_schema: bool = True) -> DataFrame:
        """Loads a file to be used when experimenting.

        To facilitate rapid iteration when experimenting we provide a method for uploading and using arbitrary parquet
        files. The purpose here is not to replace the dataset concept, but rather to enable more rapid interation
        while in the experimentation phase.
        """
        return storage.internal_experimentation_data_loader(
            absolute_data_path=self.absolute_data_path,
            experimentation_data_path=self.experimentation_data_path,
            filename=filename,
            compute_placement=self.compute_placement,
            spark_sql_context=self.spark_sql_context,
            event_manager=self.event_manager,
            merge_schema=merge_schema
        )

    def submit_result(self, result: Result):
        """ Submits a result for storage.
        Needs to be of type Result.
        """
        return self.result_manager.submit_result(result=result)

    def submit_results(self, results: List[Result]):
        """ Submits a list of results for storage.
        Needs to be of type List[Result].
        """
        return self.result_manager.submit_results(results=results)

    def to_csv(self, data_frame: DataFrame, description: str):
        """ Enables writing intermediate results to csv files
        Returns an ID for the file for downloading later
        """
        file_id = self.file_manager.save_csv_file(
            data_frame=data_frame, description=description, project_id=self.project_id, job_id=self.job_id, root_dir=self.root_dir
        )
        return file_id

    def get_data_path(self, organization_id, project_id, dataset_id):
        return 'organization_id=' + str(organization_id) + '/' + \
               'project_id=' + str(project_id) + '/' + \
               'dataset_id=' + str(dataset_id) + "/*"

    def get_experimentation_data_path(self, organization_id, project_id):
        return 'organization_id=' + str(organization_id) + '/' + \
               'project_id=' + str(project_id) + '/experimentation_files'

    def parse_filter(self, filter_json: str) -> (str, str):
        """Filters are passed as json strings to the execution manager.
        Before we proceed with script execution we transform the json to an object, and get the filter_id.
        """
        if filter_json:
            filter_dict = json.loads(filter_json)
            filter_id = filter_dict['filter_id']
        else:
            filter_id = ''  ## Necessary for later type checks
            filter_dict = None
        return filter_dict, filter_id
