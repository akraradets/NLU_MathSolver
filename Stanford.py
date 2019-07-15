from LoggerFactory import LoggerFactory
from nltk.parse.corenlp import CoreNLPDependencyParser

class Main:
    def __init__(self):
        self.logger = LoggerFactory(self).getLogger()
        self.parser = CoreNLPDependencyParser(url='http://localhost:9000')
        self.kb = {}

    def run(self, example=False):
        self.logger.debug('Starting...')
        sents = self.getInput(example)

        for sent in sents:
            self.processSent(sent)

    def processSent(self,sent):
        self.logger.info(sent)
        parsed = self.parser.parse(sent.split())
        # Have to load the object before we can read
        obj = []
        for p in parsed:
            obj = p
        self.logger.debug(obj)
        # root is always the main action
        action = obj.root
        actor = obj.get_by_address(obj.root['deps']['nsubj'][0])
        actee = obj.get_by_address(obj.root['deps']['dobj'][0])
        # self.reasoning(actor=actor, action=action, actee=actee)

    # def reasoning(self, actor, action, actee):
    #     actor_name = actor.


    def getInput(self, example):
        if example == True:
            sentences = ['Mane has 20 apples.' 
                # 'Mane gives 5 of them to Surat.', 
                # 'How many apples does Mane has?'
                ]
            self.logger.info(f'Input-Example=>{sentences}')
            return sentences
        print("Enter Text. When you are done, type Q")
        sentences = []
        while True:
            temp = (input("Enter sentence: "))
            if temp == "Q":
                break
            sentences.append(temp)
        self.logger.info(f'Input=>{sentences}')
        return sentences


main = Main()
main.run(example=True)
