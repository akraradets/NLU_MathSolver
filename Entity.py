from LoggerFactory import LoggerFactory

class Entity:
    def __init__(self,sent_obj,node):
        # we name the entity after its main lemma node
        self.name = node['lemma'].lower()
        self.index = None
        self.alias = self.name
        self.attr = set()
        # You own something from the KnowledgeBase
        self.prop = dict()
        for a in node['deps']['amod']:
            lem = sent_obj.get_by_address(a)['lemma']
            self.attr.add(lem)
        if('case' in node['deps']):
            head = sent_obj.get_by_address(node['head'])
            self.alias = head['lemma']
        # self.logger = LoggerFactory(self).getLogger()
        pass

    def updateAttr(self,node):
        self.attr = self.attr | node.attr

    def setProperty(self,item,quantity):
        # index to entity
        # quantity
        self.prop[item] = {'quantity':quantity, 'name':item}
    
    def getProperty(self,item,kb):
        property = {'quantity':None,'name':None}
        # Find property that has the same item name
        if(item in self.prop.keys()):
            # print(f'{item} found')
            print(f"{self.name} owned {item}")
            property = self.prop[item]
            return property
        else:
            # If cannot find direct name
            # Search all property in KB to see 
            for index, node in kb.memory.items():
                # I own this items
                # and this item also has alias same as I want
                if(node.name in self.prop.keys() and node.alias == item):
                    print(f"{self.name} owned {item} which is {node.name}")
                    property = self.prop[node.name]
                    print(property)
                    return property
        print(f"xxxx {self.name} didn't own {item}")
        return property

    def __str__(self):
        # dump = {'name'}
        return self.__dict__
        # return super().__str__()
