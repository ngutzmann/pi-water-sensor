LOG_CONFIG = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(name)-25s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'rotate_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': '/var/log/water-sensor.log',
            'mode': 'a',
            'maxBytes': 60*1024,  # 60KB
            'backupCount': 5
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'DEBUG'
        }
    },
    'loggers': {
        '': {
            'handlers': ['rotate_file', 'console'],
            'level': 'DEBUG'
        }
    }
}
