from LoggerFactory import LoggerFactory
from Entity import Entity

class KnowledgeBase:
    def __init__(self):
        self.logger = LoggerFactory(self).getLogger()
        # This will be the dictionary of entities
        self.memory = {}

    def get(self,index):
        # if entity is exist, return that entity, else return new entity
        if(index in self.memory):
            return self.memory[index]
        else:
            return Entity()

    def set(self,entity):
        node = self.find(entity)
        # update the node with entity
        node.updateAttr(entity)
        # save new entity to the memory with the index
        self.memory[entity.name] = node
        return node

    def find(self,entity):
        candidates = []
        for index, node in self.memory.items():
            if(node.name == entity.name):
                candidates.append(node)
        # print(candidates)
        # this is new entity
        if(len(candidates) == 0):
            self.logger.debug(f'0 [{entity.name}] found')
            return entity
        # this one candidate is the entity
        elif(len(candidates) == 1):
            self.logger.debug(f'1 [{entity.name}] found')
            return candidates[0]
        # we have more than one candidates
        # check through the candidates list for who has the best match amod
        # Best match => + if amod exist - if lack in either of lsit
        self.logger.debug(f'{len(candidates)} [{entity.name}] found')
        selected = Entity()
        max_score = -999
        # {'name': 'man', 'attr': ['tall', 'fat']}
        for cand in candidates:
            match = entity.attr & cand.attr
            unmatch = (entity.attr | cand.attr) - (entity.attr & cand.attr)
            score = len(match) - len(unmatch)
            if(score > max_score):
                max_score = score
                selected = cand
        return selected
        
    def dump(self):
        # Dump memory to the screen
        for index, node in self.memory.items():
            print(f'index={index} node={node.__dict__}')

    def reset(self):
        self.memory = {}
