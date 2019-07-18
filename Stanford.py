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
        actor = self.processEntity(obj=obj, target=actor_node)
        actee = self.processEntity(obj=obj, target=actee_node)

        # Is this a question?
        if(obj.get_by_address(1)['tag'] == 'WRB'):
            self.processQuestion()
        else:
            self.processAction(obj=obj, 
                            actorEntity=actor,
                            action=action_node,
                            actee=actee_node)
        self.kb.dump()

    def processEntity(self,obj,target):
        # create entity from the given information
        entity = Entity(sent_obj=obj,node=target)
        # Now, we set this entity into the KnowledgeBase
        entity = self.kb.set(entity)
        return entity

    def processAction(self,obj,actorEntity,action,actee):
        own = {'have'}
        add = {'get'}
        sub = {}
        quantity = 'some'
        # Extract Quantity from the sentence
        if('nummod' in actee['deps']):
            CD = obj.get_by_address(actee['deps']['nummod'][0])
            quantity = int(CD['lemma'])

        # create property to actor
        if(action['lemma'] in own):
            actorEntity.setProperty(actee['lemma'], quantity)
        # add more of the property t the actor
        elif(action['lemma'] in add):
            number = actorEntity.getProperty(actee['lemma'])['quantity']
            number = number + quantity
            actorEntity.setProperty(actee['lemma'], number)
            pass
        
    def getInput(self, example):
        if example == True:
            sentences = ["The dog has 7 bones.", 
            "Dog gets 3 more bones.", 
            # "How many bones altogether?"
            "How many bones does the dog have?"
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
