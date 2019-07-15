from LoggerFactory import LoggerFactory

class Entity:
    def __init__(self):
        self.logger = LoggerFactory(self).getLogger()
