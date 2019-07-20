from LoggerFactory import LoggerFactory
from KnowledgeBase import KnowledgeBase
from Entity import Entity
from nltk.parse.corenlp import CoreNLPDependencyParser

class Main:
    def __init__(self):
        self.logger = LoggerFactory(self).getLogger()
        self.parser = CoreNLPDependencyParser(url='http://localhost:9000')
        self.lastEntity = {}
        self.kb = KnowledgeBase()

    def run(self, mode=9, target=-1, start=0, end=10000):
        self.logger.debug('Starting...')

        sentences = []
        if(mode == 0):
            # normal input mode
            sentences = self.getInput()
            for sent in sentences:
                self.processSent(sent)
        elif(mode == 9):
            # example mode
            self.logger.info('run with Example Mode')
            sentences = ["The old man has 10 red balls.", 
                         "The man gives 3 balls away.",
                        # "How many bones altogether?"
                        "How many balls does the tall man have?"
                ]
            self.logger.info(f'Input-Example=>{sentences}')
            for sent in sentences:
                self.processSent(sent)
        elif(mode == 10):
            # run dataset
            from nltk.tokenize import sent_tokenize
            self.logger.info('run with Dataset Mode')
            dataset = self.getDataset()
            # Target is for which dataset number you want to test with
            if(target >= 0):
                dataset = [dataset[target]]
            start = 10
            for i in range(start, end):
            # for data in dataset:
                data = dataset[i]
                sentences = sent_tokenize(data['Question'])
                answer = data['Answer']
                # before we process each set, we reset the KnowledgeBase
                self.kb.reset()
                self.lastEntity = {}
                # process the sentences nomally
                for sent in sentences:
                    self.processSent(sent)
                print(f'[{i}] {data["Question"]}')
                print(f'DatasetAnswer={answer}|BotAnswer={self.dataset_answer}')
                input("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                

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
        actee_node = 'None-DOBJ'
        if('dobj' in obj.root['deps']):
            actee_node = obj.get_by_address(obj.root['deps']['dobj'][0])
            # [actee] of [real object]
            if('nmod' in actee_node['deps']):
                actee_node = obj.get_by_address(actee_node['deps']['nmod'][0])
        # KB management
        print("-------- LastEntity --------")
        for type, o in self.lastEntity.items():
            print(f'Type={type} Count={o["count"]} Entity={o["entity"].__dict__ }')
        print("======== LastEntity ========")
        actor = self.processEntity(obj=obj, target=actor_node)
        actee = self.processEntity(obj=obj, target=actee_node)
        # print('aaaaaaaaaaaaaaaaa ',actee.__dict__)
        # Is this a question?
        if(obj.get_by_address(1)['tag'] in {'WRB', 'WP'}):
            # WRB => HOW
            # WP => WHO
            self.logger.debug('This is question')
            self.processQuestion(obj,actor,action_node,actee_node)
        else:
            self.logger.debug('This is sentence')
            self.processAction(obj=obj, 
                            actorEntity=actor,
                            action=action_node,
                            actee=actee_node)

        # Never set lastEntity
        if(len(self.lastEntity) == 0):
            self.lastEntity['actor'] = {'count': 0, 'entity': actor}
            self.lastEntity['actee'] = {'count': 0, 'entity': actee}
        else:
            # never use this to refer => reset
            if(self.lastEntity['actor']['count'] == 0):
                self.lastEntity['actor'] = {'count': 0, 'entity': actor}
            if(self.lastEntity['actee']['count'] == 0):
                self.lastEntity['actee'] = {'count': 0, 'entity': actee}

        print("-------- KnowledgeBase --------")
        self.kb.dump()
        print("======== KnowledgeBase ========")

    def processEntity(self,obj,target):
        # How many does she eat
        # No dobj to eat
        # This also refer to previous actee
        if(target == 'None-DOBJ'):
            self.lastEntity['actee']['count'] = self.lastEntity['actee']['count'] + 1
            entity = self.lastEntity['actee']['entity']
            self.logger.debug(f'{target} means {entity.name}')
            return entity
        #  If already processed 1 sentence before
        # And we try to refer something this time
        if(len(self.lastEntity) != 0):
            if(target['lemma'] in {'he','she'}):
                self.lastEntity['actor']['count'] = self.lastEntity['actor']['count'] + 1
                entity = self.lastEntity['actor']['entity']
                self.logger.debug(f'{target["lemma"]} means {entity.name}')
                return entity
            # she eats 7 more
            # more refer to previous actee
            elif(target['lemma'] in {'more'}):
                self.lastEntity['actee']['count'] = self.lastEntity['actee']['count'] + 1
                entity = self.lastEntity['actee']['entity']
                self.logger.debug(f'{target["lemma"]} means {entity.name}')
                return entity

        # create entity from the given information
        entity = Entity(sent_obj=obj,node=target)
        # Now, we set this entity into the KnowledgeBase
        entity = self.kb.set(entity)
        return entity

    def processQuestion(self, obj, actorEntity, action, actee):
        own = {'have', 'eat', 'buy'}
        answer = ''
        # There are many type of question
        tag = obj.get_by_address(1)['tag']
        if(tag == 'WP'):
            # Ask for a person
            # start with who => tag:WP
            if(action['lemma'] in own):
                import math
                # someone owns actee
                gt = {'[more]','greater'}
                lt = {'[less]', 'least'}
                gt_temp = -math.inf
                lt_temp = math.inf
                entity = None
                property = actee['lemma']
                # number of [actee]
                if('case' in actee['deps']):
                    head = obj.get_by_address(actee['head'])
                    comparator = obj.get_by_address(head['deps']['amod'][0])['lemma']
                    # self.logger.info(f'Who has {comparator} {actee["lemma"]} of {property}')
                # [more|less] [actee]
                else:
                    if('amod' in actee['deps']):
                        for amod_index in actee['deps']['amod']:
                            amod = obj.get_by_address(amod_index)
                            if(amod['lemma'] == 'more'):
                                comparator = '[more]'
                            if(amod['lemma'] == 'less'):
                                comparator = '[less]'
                    

                for index, node in self.kb.memory.items():
                    number = node.getProperty(property,self.kb)['quantity']
                    if(number == None): continue
                    if(comparator in gt and number >= gt_temp):
                        entity = node
                        gt_temp = number
                    elif(comparator in lt and number <= lt_temp):
                        entity = node
                        lt_temp = number
                self.dataset_answer = entity.name
                print(f'ANSWER=>"{entity.name}"')
        elif(tag == 'WRB'):
            # Ask for a number
            # start with How many
            quantity = ''
            # create property to actor
            if(action['lemma'] in own):
                if(actee == 'None-DOBJ'):
                    property = self.lastEntity['actee']['entity'].name
                else:
                    property = actee['lemma']
                    
                number = actorEntity.getProperty(property,self.kb)['quantity']
                subj = self.construct(obj, 'nsubj')
                if(actee == 'None-DOBJ'):
                    dobj = property
                else:
                    if(number > 1):
                        dobj = self.construct(obj, 'dobj', True)
                    else:
                        dobj = self.construct(obj, 'dobj')
                self.dataset_answer = number
                print(f'ANSWER=>"{subj} {action["word"]} {number} {dobj}"')

    def construct(self, obj, target, plural = False):
        ret = ''
        main = obj.get_by_address(obj.root['deps'][target][0])
        if('det' in main['deps']):
            ret = ret + obj.get_by_address(main['deps']['det'][0])['lemma'] + " "

        if('amod' in main['deps']):
            for amod in main['deps']['amod']:
                if(obj.get_by_address(amod)['lemma'] != "many"):
                    ret = ret + obj.get_by_address(amod)['lemma'] + " "
        
        ret = ret + main['lemma']

        if(plural):
            ret = ret + 's'

        if('nmod' in main['deps']):
            ret = ret + " of " + obj.get_by_address(main['deps']['nmod'][0])['lemma']
        return ret                

    def processAction(self,obj,actorEntity,action,actee):
        own = {'have', 'eat', 'buy'}
        add = {'[more]', 'get'}
        sub = {'[less]', 'give'}
        quantity = 'some'
        verb = action['lemma']
        # Extract Quantity from the sentence
        # 3 [head] of [actee]
        if(actee['rel'] == 'nmod'):
            self.logger.debug("[Search for head]")
            head = obj.get_by_address(actee['head'])
            CD = obj.get_by_address(head['deps']['nummod'][0])
            quantity = int(CD['lemma'])
            # [black] ears of corn
            # 3 [more] [black] ears of corn
            if('amod' in head['deps']):
                for amod_index in head['deps']['amod']:
                    amod = obj.get_by_address(amod_index)
                    if(amod['lemma'] == 'more'):
                        verb = '[more]'
                    if(amod['lemma'] == 'less'):
                        verb = '[less]'
        else:
            # 3 [actee]
            self.logger.debug("[This is head]")
            if('nummod' in actee['deps']):
                CD = obj.get_by_address(actee['deps']['nummod'][0])
                quantity = int(CD['lemma'])
            # 3 [more|less] ears
            if('amod' in actee['deps']):
                for amod_index in actee['deps']['amod']:
                    amod = obj.get_by_address(amod_index)
                    if(amod['lemma'] == 'more'):
                        verb = '[more]'
                    if(amod['lemma'] == 'less'):
                        verb = '[less]'
            if(actee['lemma'] == 'more'):
                actee['lemma'] = self.lastEntity['actee']['entity'].name
                verb = '[more]'
            if(actee['lemma'] == 'less'):
                actee['lemma'] = self.lastEntity['actee']['entity'].name
                verb = '[less]'

        # create property to actor
        if(verb in own):
            self.logger.debug("[OWN]")
            actorEntity.setProperty(actee['lemma'], quantity)
        # add more of the property t the actor
        elif(verb in add):
            self.logger.debug("[ADD]")
            item = actorEntity.getProperty(actee['lemma'],self.kb)
            number = item['quantity'] + quantity
            actorEntity.setProperty(item['name'], number)
        elif(verb in sub):
            self.logger.debug("[SUB]")
            item = actorEntity.getProperty(actee['lemma'], self.kb)
            number = item['quantity'] - quantity
            actorEntity.setProperty(item['name'], number)

    def getInput(self):
        print("Enter Text. When you are done, type Q")
        sentences = []
        while True:
            temp = (input("Enter sentence: "))
            if temp == "Q":
                break
            sentences.append(temp)
        self.logger.info(f'Input=>{sentences}')
        return sentences

    def getDataset(self):
        import json
        filename = 'MathDict/data.json'
        if filename:
            with open(filename, 'r') as f:
                datastore = json.load(f)
        return datastore

main = Main()
# mode 0 = normal
# main.run()
# mode 9 = example
# main.run(mode=9)
# mode 10 = dataset 
main.run(mode=10,start=0)
