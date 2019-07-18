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
            self.processQuestion(obj,actor,action_node,actee_node)
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

    def processQuestion(self, obj, actorEntity, action, actee):
        own = {'have'}
        quantity = ''
        answer = ''
        # create property to actor
        if(action['lemma'] in own):
            number = actorEntity.getProperty(actee['lemma'])['quantity']
            subj = self.construct(obj, 'nsubj')
            dobj = self.construct(obj, 'dobj')
            if(number > 1):
                dobj = dobj+'s'
            print(f'ANSWER=>"{subj} {action["word"]} {number} {dobj}"')

    def construct(self, obj, target):
        ret = ''
        main = obj.get_by_address(obj.root['deps'][target][0])
        if('det' in main['deps']):
            ret = ret + obj.get_by_address(main['deps']['det'][0])['lemma'] + " "
        if('amod' in main['deps']):
            for amod in main['deps']['amod']:
                if(obj.get_by_address(amod)['lemma'] != "many"):
                    ret = ret + obj.get_by_address(amod)['lemma'] + " "
        ret = ret + main['lemma']
        return ret                

    def processAction(self,obj,actorEntity,action,actee):
        own = {'have'}
        add = {'get', 'buy'}
        sub = {'give'}
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
        elif(action['lemma'] in sub):
            number = actorEntity.getProperty(actee['lemma'])['quantity']
            number = number - quantity
            actorEntity.setProperty(actee['lemma'], number)           

    def getInput(self, example):
        if example == True:
            sentences = ["The old man has 10 red balls.", 
                         "The man gives 3 balls away.",
                        # "How many bones altogether?"
                        "How many balls does the tall man have?"
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
