import logging
# logging.debug('This is a debug message')
# logging.info('This is an info message')
# logging.warning('This is a warning message')
# logging.error('This is an error message')
# logging.critical('This is a critical message')


class Logger:
    def __init__(self, className):
        logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s', filename='log.txt',
                            datefmt='%Y%m%d %H:%M:%S', level=logging.DEBUG)
        logging.getLogger().addHandler(logging.StreamHandler())
        self.className = className

    def log(self, level, message):
        if level not in ["debug", "info", "warning", "error", "critical"]:
            raise Exception(
                "Logger level on accept [debug,info,warning,error,critical].")
        result = getattr(logging, level)(
            f'class={self.className}|message={message}')

# logger = Logger("Logger")
# logger.log("debug", 'Test Message')
