from systems.LoggerFactory import LoggerFactory
from nltk.parse.corenlp import CoreNLPDependencyParser
from nltk.parse.corenlp import CoreNLPParser
from nltk.tree import ParentedTree
import nltk
import SRL

class Main:
    def __init__(self):
        self.logger = LoggerFactory(self).getLogger()

    def run(self, mode=0, target=-1, start=1, end=10000):
        self.logger.debug('Starting...')
        


main = Main()
main.run()
# main.run()
