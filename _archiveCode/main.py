from systems.LoggerFactory import LoggerFactory
from nltk.parse.corenlp import CoreNLPDependencyParser
from nltk.parse.corenlp import CoreNLPParser
from nltk.tree import ParentedTree
import nltk

class Main:
    def __init__(self):
        self.logger = LoggerFactory(self).getLogger()
        self.depenParser = CoreNLPDependencyParser(url='http://localhost:9000')
        self.treeParser = CoreNLPParser('http://localhost:9000')
        self.dataset_answer = None
        self.v3 = nltk.corpus.util.LazyCorpusLoader(
            'verbnet3', nltk.corpus.reader.verbnet.VerbnetCorpusReader,
            r'(?!\.).*\.xml')
        self.verbTagList = ["VB","VBD","VBG","VBN","VBP","VBZ"]

    def run(self, mode=0, target=-1, start=1, end=10000):
        self.logger.debug('Starting...')
        sentences = []
        sentences.append("There are 5 fishes.")
        for sent in sentences:
            self.processSentence(sent)
    
    def processSentence(self,sent):
        self.logger.info(sent)
        dependencyTree = self.depenParser.parse(sent.split())
        parseTree = self.treeParser.parse(sent.split())
        # Have to load the object before we can read
        depenObj = []
        for p in dependencyTree:
            depenObj = p
        self.logger.debug(depenObj)
        treeObj = []

        for p in parseTree:
            treeObj = p
        self.logger.debug(treeObj)
        ptree = ParentedTree.fromstring(treeObj.pformat())
        self.traverse(ptree)
        # root is always the main action
        root = depenObj.root
        # check if root is verb
        if(root['tag'] not in self.verbTagList):
            self.logger.error(f'root is not a verb')
            self.logger.debug(f'{root}')
        
        # load semantic
        lemma = root['lemma']
        classList = self.v3.classids(lemma)
        for c in classList:
            self.logger.info(f'lemma:{lemma}|class:{c}')
            vn = self.v3.vnclass(c)
            self.logger.info(self.v3.pprint(vn))

    def traverse(self,t):
        try:
            t.label()
        except AttributeError:
            return
        else:
            if t.height() == 2:   #child nodes
                print(t.parent())
                return
            for child in t:
                self.traverse(child)

main = Main()
main.run()
# main.run()
