import sys

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[{asctime}] #{levelname:8} {filename}:{lineno} - {name} - {message}',
            'style': '{'
        }
    },
    'handlers': {
        'file_handler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'default',
            'filename': 'log/log',
            'when': 'D',
            'interval': 7,
            'backupCount': 5,
            'level': 'INFO',
            'encoding': 'utf-8'
        },
        'console_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'INFO',
            'stream': sys.stdout
        }
    },
    'loggers': {
        'database': {
            'level': 'DEBUG',
            'handlers': ['file_handler', 'console_handler']
        }
    },
    'root': {
        'level': 'DEBUG',
        'formatter': 'default',
        'handlers': ['file_handler', 'console_handler']
    }
}

