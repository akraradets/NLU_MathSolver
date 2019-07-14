from LoggerFactory import LoggerFactory

class Main:
    def __init__(self):
        self.logger = LoggerFactory(self).getLogger()
