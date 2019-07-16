from LoggerFactory import LoggerFactory

class Entity:
    def __init__(self,sent_obj,node):
        # we name the entity after its main lemma node
        self.name = node['lemma'].lower()
        self.attr = set()
        for a in node['deps']['amod']:
            lem = sent_obj.get_by_address(a)['lemma']
            self.attr.add(lem)
        # self.logger = LoggerFactory(self).getLogger()
        pass

    def update(self,node):
        self.attr = self.attr | node.attr

    # def setup(self,node):
    #     self.name = node['lemma']

    def __str__(self):
        # dump = {'name'}
        return self.__dict__
        # return super().__str__()
