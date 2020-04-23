import logging
import sys

def setup_logging() -> type(logging.log):
    FORMAT = '%(asctime)-15s %(levelname)-5s [%(name)-20s] %(message)s'
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARN)
    logging.basicConfig(format=FORMAT, stream=sys.stdout)
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    return log


def get_logger():
    return logging.getLogger(__name__)
