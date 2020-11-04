import logging
import sys


def setup_logging() -> type(logging.log):
    FORMAT = '%(asctime)-15s %(levelname)-1s [%(name)-10s] %(message)s'
    logging.basicConfig(format=FORMAT, stream=sys.stdout)
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    return log


def get_logger():
    return logging.getLogger(__name__)
