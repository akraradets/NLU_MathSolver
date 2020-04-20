from systems.LoggerFactory import LoggerFactory
from allennlp.predictors.predictor import Predictor
from ConParser import ConParser
from MSCorpus import ProblemClass

class SRL:
  __instance = None
  
  @staticmethod 
  def getInstance():
    if SRL.__instance == None:
        SRL()
    return SRL.__instance

  def __init__(self):
    if SRL.__instance != None:
        raise Exception("This class is a Singleton!")
    else:
        self.logger = LoggerFactory(self).getLogger()
        self.predictor = Predictor.from_path("libs/allennlp-SRL.tar.gz")
        SRL.__instance = self

  def parse(self, sentence):
    # reset results
    self.results = None
    results = self.predictor.predict(
      sentence=sentence
    )
    # save results
    self.results = results

    words = results['words']
    verbs = []
    verbs_aux = []
    tags = {}
    roles = {}

    for target in results['verbs']:
      tagged_words = []
      roles_set = set()
      isAux = False
      if len(target['tags']) == target['tags'].count('O') + 1:
        isAux = True
      
      # if isAux and withAux == False:
      #   continue

      for word, tag in zip(words, target['tags']):
        suffix = ''
        role = tag
        if tag.find('-') >= 0:
          suffix, role = tag.split('-',1)

        tag = {'word':word,
          'tag':tag,
          'suffix': suffix,
          'role': role}
        tagged_words.append(tag)
        roles_set.add(role)

      if(isAux == False):
        verbs.append(target['verb'])
      verbs_aux.append(target['verb'])
      tags[target['verb']] = tagged_words
      roles[target['verb']] = roles_set

    self.words = words
    self.verbs = verbs
    self.verbs_aux = verbs_aux
    self.tags = tags
    self.roles = roles

    return self.verbs

  def getRealVerb(self,pos):
    verbs_aux = set(self.verbs_aux)
    obj = {"isExist": False, "word": None, "index":None, "pos":None}
    self.obj_do = obj.copy()
    self.obj_have = obj.copy()
    self.obj_real_verb = obj.copy()

    set_do = ProblemClass.SET_DO
    set_have = ProblemClass.SET_HAVE
    set_label_verb = ConParser.SET_LABEL_VERB
    words = self.words
    real_verb = ""

    if(set_do.isdisjoint(verbs_aux) == False):
      self.obj_do["word"] = set_do.intersection(verbs_aux).pop()
      self.obj_do["isExist"] = True
      self.obj_do["index"] = words.index(self.obj_do["word"])
      self.obj_do["pos"] = pos[self.obj_do["index"]]
      self.logger.debug(f"Found do:{self.obj_do}")
    if(set_have.isdisjoint(verbs_aux) == False):
      # if have is real verb or an aux?
      self.obj_have["word"] = set_have.intersection(verbs_aux).pop()
      self.obj_have["isExist"] = True
      self.obj_have["index"] = words.index(self.obj_have["word"])
      self.obj_have["pos"] = pos[self.obj_have["index"]]
      self.logger.debug(f"Found have:{self.obj_have}")
      if(pos[self.obj_have["index"] + 1] in set_label_verb):
        real_verb = words[self.obj_have["index"] + 1]
      else:
        real_verb = self.obj_have["word"]

    if(real_verb == ""):
      # if have not exist, reverb is set(aux)-set_do
      real_verb = verbs_aux.difference(set_do).pop()

    self.logger.debug(f"Found real_verb:{real_verb}")
    return real_verb

  def getRoleSet(self, verb):
    role_set = []
    try:
      role_set = self.roles[verb]
    except KeyError:
      raise KeyError(f"{verb} is not found in {self.verbs}. \n The sentence is {self.words}")

    return role_set

  def getRole(self, role, verb, suffix = None):
    # return an array of word that tagged as the query role and verb
    tagged_words = []

    try:
      tagged_words = self.tags[verb]
    except KeyError:
      raise KeyError(f"{verb} is not found in {self.verbs}. \n The sentence is {self.words}")

    # print(tagged_words)

    output = []
    for tagged_word in tagged_words:
      # print(tagged_word)
      if(tagged_word['role'] == role):
        output.append(tagged_word['word'])

    return output

# print("== Role ==")
# print(srl.getRoleSet('think'))
# print("==== think ====")
# print(srl.getRole('ARG0','think'))
# print(srl.getRole('ARG1','think'))
# print("==== beat ====")
# print(srl.getRole('ARG0','beat'))
# print(srl.getRole('ARG1','beat'))