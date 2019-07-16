from LoggerFactory import LoggerFactory
from KnowledgeBase import KnowledgeBase
from Entity import Entity
from nltk.parse.corenlp import CoreNLPDependencyParser

class Main:
    def __init__(self):
        self.logger = LoggerFactory(self).getLogger()
        self.parser = CoreNLPDependencyParser(url='http://localhost:9000')
        self.kb = KnowledgeBase()

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
        action_node = obj.root
        actor_node = obj.get_by_address(obj.root['deps']['nsubj'][0])
        actee_node = obj.get_by_address(obj.root['deps']['dobj'][0])
        # KB management
        self.processEntity(obj=obj, target=actor_node)
        self.processEntity(obj=obj, target=actee_node)
        self.kb.dump()
        # print("END")
        # Actor
        # entity = self.kb.get(actor['lemma'])
        # entity.setup(actor)
        # self.kb.set(index=actor['lemma'],entity=entity)
        # # Actee
        # entity = self.kb.get(actee['lemma'])
        # entity.setup(actee)
        # self.kb.set(index=actee['lemma'], entity=entity)
        # # Action

    def processEntity(self,obj,target):
        # create entity from the given information
        entity = Entity(sent_obj=obj,node=target)
        # Now, we set this entity into the KnowledgeBase
        self.kb.set(entity)


    def getInput(self, example):
        if example == True:
            sentences = ['The tall fat man has 20 good apples.'
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
