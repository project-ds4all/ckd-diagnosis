import logging


class LoggingUtils:
    @classmethod
    def initialize(cls) -> None:
        logging_mode = logging.INFO
        logging.basicConfig(format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
                            level=logging_mode)
