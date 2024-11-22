import logging


class ErrorLog(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.ERROR


class DebugLog(logging.Filter):
    def filter(self, record):
        return record.levelname == 'DEBUG'
