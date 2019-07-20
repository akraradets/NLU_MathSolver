from LoggerFactory import LoggerFactory

class Entity:
    def __init__(self,sent_obj,node):
        # we name the entity after its main lemma node
        self.name = node['lemma'].lower()
        self.attr = set()
        # You own something from the KnowledgeBase
        self.prop = dict()
        for a in node['deps']['amod']:
            lem = sent_obj.get_by_address(a)['lemma']
            self.attr.add(lem)
        # self.logger = LoggerFactory(self).getLogger()
        pass

    def updateAttr(self,node):
        self.attr = self.attr | node.attr

    def setProperty(self,item,quantity):
        # index to entity
        # quantity
        self.prop[item] = {'quantity':quantity}
    
    def getProperty(self,item):
        # print(f'Finnding {item} in {self.prop.keys()}')

        property = {'quantity':None}
        if(item in self.prop.keys()):
            # print(f'{item} found')
            property = self.prop[item]
        return property

    def __str__(self):
        # dump = {'name'}
        return self.__dict__
        # return super().__str__()
