import logging

CLOUD_LOGGING = True
try:
    from google.cloud import logging as stackdriver
except:
    CLOUD_LOGGING = False
    print("*WARNING* Not logging to stackdriver.")

FORMAT = '[%(asctime)-15s] [%(name)-25s] [%(levelname)-8s] %(message)s'


class AnnotellLogger:

    @staticmethod
    def get_logger(name, threshold=logging.DEBUG, send=False):
        logging.basicConfig(format=FORMAT)
        logger = logging.getLogger(name)
        logger.setLevel(threshold)
        if CLOUD_LOGGING and send:
            logger.info("adding google cloud stackdriver handler")
            client = stackdriver.Client()
            handler = client.get_default_handler()
            logger.addHandler(handler)
        return logger
