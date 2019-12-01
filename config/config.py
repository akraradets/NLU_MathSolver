import glob
from LoggerFactory import LoggerFactory

class Config:
    # envi can be ['local']
    envi = 'local'
    def __init__(self):
        self.logger = LoggerFactory(self).getLogger()

    def run(self):
        if(self.isEnviExist(self.envi) == False):
            raise ConfigError(f'Environment "{self.envi}" not exist!')
        self.logger.info(f'Loading "{self.envi}" configuration')

    def isEnviExist(self,envi):
        isExist = False
        for folder in glob.glob('./**/'):
            if(folder == f'./{envi}/'):
                isExist = True
                break
        return isExist

class ConfigError(ValueError):
    pass

config = Config()
config.run()