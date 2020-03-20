from execution_manager import ExecutionManager
import time

execution_manager = ExecutionManager(kpi_manager_host='http://localhost:5000')

execution_manager.submit_event(123, 'load_data', '')
