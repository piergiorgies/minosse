from src.config_loader import load_config
from logging_loki import LokiQueueHandler
from multiprocessing import Queue
import logging


config = load_config()

class LokiLogger:
    def __init__(self):
        self.name = config.name
        self.url = config.loki_url
        self.level = config.log_level
        self.CONSOLE_LOG = config.console_log
        self._configure_logging()

    def _configure_logging(self):
        loki_handler = LokiQueueHandler(
            Queue(-1),
            url=self.url,
            tags={"application": self.name},
            version="1"
        )

        handlers = [loki_handler]
        if self.CONSOLE_LOG:
            console_handler = logging.StreamHandler()
            handlers.append(console_handler)
        
        # Configura il logger
        logging.basicConfig(
            level=self.level,
            handlers=handlers,
            format="%(levelname)s - %(name)s - %(message)s"
        )

        logging.getLogger("urllib3").setLevel(logging.WARNING)

        self.logger = logging.getLogger(self.name)

    def get_logger(self):
        return self.logger
    

logger_instance = None

def get_logger():
    global logger_instance
    if logger_instance is None:
        logger_instance = LokiLogger()
    return logger_instance.get_logger()