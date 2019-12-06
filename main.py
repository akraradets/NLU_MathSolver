from systems.LoggerFactory import LoggerFactory
from nltk.parse.corenlp import CoreNLPDependencyParser

class Main:
    def __init__(self):
        self.logger = LoggerFactory(self).getLogger()
        self.parser = CoreNLPDependencyParser(url='http://localhost:9000')
        self.dataset_answer = None

        self.verbTagList = ["VB","VBD","VBG","VBN","VBP","VBZ"]

    def run(self, mode=0, target=-1, start=1, end=10000):
        self.logger.debug('Starting...')
        sentences = []
        sentences.append("Sue drinks 3 carrots.")
        for sent in sentences:
            self.processSentence(sent)
    
    def processSentence(self,sent):
        self.logger.info(sent)
        parsed = self.parser.parse(sent.split())
        # Have to load the object before we can read
        obj = []
        for p in parsed:
            obj = p
        self.logger.debug(obj)

        # root is always the main action
        root = obj.root
        # check if root is verb
        if(root['tag'] not in self.verbTagList):
            self.logger.error(f'root is not a verb')
            self.logger.debug(f'{root}')
        

main = Main()
main.run()
# main.run()
