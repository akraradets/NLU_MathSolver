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

# sent = "How many apples did Sam have?"
sent = "How many apples did Sam have this breakfast?"
# sent = "How many apples does Sam have left?"

from ConParser import ConParser
cParser = ConParser.getInstance()
pos = cParser.parse(sent)
print(cParser.words)
print(pos)

srl = SRL.getInstance()
verbs = srl.parse(sent)
print(srl.verbs_aux)
print(srl.tags['have'])
# print(srl.results)
# print(srl.getRole('have'))


# It coexists with an eatable object.
# The sentence is not in the present simple tense.
# If the sentence is the present simple tense, It must have an adverb of frequency.
# It is the answer to the previous sentence that met the conditions.

list_do = ['do','does','did']
list_have = ['have', 'has', 'had']
list_label_verb = ['VB','VBD','VBG','VBN','VBP','VBZ']
if(set(list_do).isdisjoint(set(srl.verbs_aux)) == False):
  print('contains do did does')
if(set(list_have).isdisjoint(set(srl.verbs_aux)) == False):
  print('contains has have had')
  # if have is real verb or an aux?
  have = set(list_have).intersection(set(srl.verbs_aux)).pop()
  print(have)
  index = cParser.words.index(have)
  if(pos[index + 1] in list_label_verb):
    print("Have is an aux")
    real_verb = cParser.words[index + 1]
  else:
    print("Have is not an aux")
    real_verb = have

print(real_verb)

# print("== Role ==")
# print(srl.getRoleSet('think'))
# print("==== think ====")
# print(srl.getRole('ARG0','think'))
# print(srl.getRole('ARG1','think'))
# print("==== beat ====")
# print(srl.getRole('ARG0','beat'))
# print(srl.getRole('ARG1','beat'))