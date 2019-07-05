import logging
# logging.debug('This is a debug message')
# logging.info('This is an info message')
# logging.warning('This is a warning message')
# logging.error('This is an error message')
# logging.critical('This is a critical message')

class Logger:
    def __init__(self, className):
        logging.basicConfig(format='%(asctime)s - %(message)s',
                            datefmt='%Y%m%d %H:%M:%S', level=logging.DEBUG)
        self.className = className

    def log(self, level, message):

        if level not in ["debug", "info", "warning", "error", "critical"]:
            print('asd')
            raise Exception(
                "Logger level on accept [debug,info,warning,error,critical].")
        result = getattr(logging, level)(
            "class="+self.className + "|message=" + message)


# logger = Logger("Logger")
# logger.log("debug", 'Test Message')
