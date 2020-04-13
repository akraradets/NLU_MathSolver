from systems.LoggerFactory import LoggerFactory
from allennlp.predictors.predictor import Predictor

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

  def parse(self, sentence, withAux = False):
    # reset results
    self.results = None
    results = self.predictor.predict(
      sentence=sentence
    )
    # save results
    self.results = results

    words = results['words']
    verbs = []
    tags = {}
    roles = {}

    for target in results['verbs']:
      tagged_words = []
      roles_set = set()
      isAux = False
      if len(target['tags']) == target['tags'].count('O') + 1:
        isAux = True
      
      if isAux and withAux == False:
        continue

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

      verbs.append(target['verb'])
      tags[target['verb']] = tagged_words
      roles[target['verb']] = roles_set

    self.words = words
    self.verbs = verbs
    self.tags = tags
    self.roles = roles

    return self.verbs
  
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
    # return 'e'

# srl = SRL.getInstance()
# verbs = srl.parse("Did Uriah honestly think he could beat The Legend of Zelda in under three hours?")
# print(verbs)
# print("== Role ==")
# print(srl.getRoleSet('think'))
# print("==== think ====")
# print(srl.getRole('ARG0','think'))
# print(srl.getRole('ARG1','think'))
# print("==== beat ====")
# print(srl.getRole('ARG0','beat'))
# print(srl.getRole('ARG1','beat'))