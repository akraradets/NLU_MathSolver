from systems.LoggerFactory import LoggerFactory
from MSParser import ConParser
from MSCorpus import WordSem
import json

class Entity:

  UNKNOWN = -1

  TYPE_HUMAN = 0
  TYPE_OBJECT = 1
  TYPE_REF_GENDER_MALE = 2
  TYPE_REF_GENDER_FEMALE = 3
  TYPE_REF_GROUP = 4
  LIST_TYPE = {
   -1 : 'UNKNOWN',
    0 : 'HUMAN',
    1 : 'OBJECT',
    2 : 'REF_GENDER_MALE',
    3 : 'REF_GENDER_FEMALE',
    4 : 'REF_GROUP'
  }

  GENDER_MALE = 0
  GENDER_FEMALE = 1
  LIST_GENDER = {
   -1 : 'UNKNOW',
    0 : 'MALE',
    1 : 'FEMALE'
  }

  def __init__(self,wordArray):
    self.logger = LoggerFactory(self).getLogger()

    self.quantity = None
    self.adjective = set()
    self.name = None
    self.type = Entity.UNKNOWN
    self.gender = Entity.UNKNOWN
    for w in wordArray:
      if(w.pos == 'CD'): self.quantity = w.name
      elif(w.pos == 'JJ'): self.adjective.add(w.name.lower())
      # A Pronoun [I, You, We, They, ...]
      elif(w.pos == 'PRP'):
        self.name = w.lemma.lower()
        if(w.name.lower() == 'they'): self.type = Entity.TYPE_REF_GROUP
        elif(w.name.lower() == 'he'): self.type = Entity.TYPE_REF_GENDER_MALE
        elif(w.name.lower() == 'she'): self.type = Entity.TYPE_REF_GENDER_FEMALE
      elif(w.pos in ConParser.SET_LABEL_NOUN):
        self.name = w.lemma.lower()
        self.type = Entity.TYPE_OBJECT
        # A proper Noun
        if(w.pos == 'NNP'):
          # print(WordSem.SET_PERSON_MALE)
          # print(w.name.upper() in WordSem.SET_PERSON_MALE)
          # check if it in the set of human common name
          if(w.name.upper() in WordSem.SET_PERSON_MALE):
            self.type = Entity.TYPE_HUMAN
            self.gender = Entity.GENDER_MALE
          elif(w.name.upper() in WordSem.SET_PERSON_FEMALE):  
            self.type = Entity.TYPE_HUMAN
            self.gender = Entity.GENDER_FEMALE

  def getTypeName(self):
    return Entity.LIST_TYPE.get(self.type, "Invalid numbner")
  
  def getGenderName(self):
    return Entity.LIST_GENDER.get(self.gender, "Invalid numbner")

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    obj = {}
    obj['quantity'] = self.quantity
    obj['adjective'] = list(self.adjective)
    obj['name'] = self.name
    obj['type'] = self.getTypeName()
    if(self.type == Entity.TYPE_HUMAN): obj['gender'] = self.getGenderName()
    return json.dumps(obj)