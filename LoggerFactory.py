import logging
# logging.debug('This is a debug message')
# logging.info('This is an info message')
# logging.warning('This is a warning message')
# logging.error('This is an error message')
# logging.critical('This is a critical message')


class LoggerFactory:
    def __init__(self, callerClass):
        format = '%(asctime)s-%(name)s(%(funcName)s)-%(levelname)s|%(message)s'
        file = 'log.txt'
        dateFormat = '%Y%m%d %H:%M:%S'
        logging.basicConfig(format=format, filename=file, datefmt=dateFormat)
        self.logger = logging.getLogger(callerClass.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(fmt=format)
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)

        self.logger.addHandler(streamHandler)

    def getLogger(self):
        return self.logger

# logger = LoggerFactory("Logger").getLogger()
# logger.info('Test Message')
