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
        node.update(entity)
        # save new entity to the memory with the index
        self.memory[entity.name] = entity

    def find(self,entity):
        candidates = []
        for index, node in self.memory.items():
            if(node.name == entity.name):
                candidates.append(node)
        # print(candidates)
        # this is new entity
        if(len(candidates) == 0):
            return entity
        # this one candidate is the entity
        elif(len(candidates) == 1):
            return candidates[0]
        # we have more than one candidates
        # check through the candidates list for who has the best match amod
        # Best match => + if amod exist - if lack in either of lsit
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
