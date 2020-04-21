from systems.LoggerFactory import LoggerFactory
from allennlp.predictors.predictor import Predictor
from nltk.tokenize import word_tokenize

from MSCorpus import ProblemClass

""" ConstituencyParser """
class ConParser:
  __instance = None

  SET_LABEL_QUERY = set({'WRB'})  
  SET_LABEL_VERB = set({'VB','VBD','VBG','VBN','VBP','VBZ'})
  SET_LABEL_NOUN = set({'NN','NNS','NNP','NNPS'})

  @staticmethod 
  def getInstance():
    if ConParser.__instance == None:
      ConParser()
    return ConParser.__instance

  def __init__(self):
    if ConParser.__instance != None:
      raise Exception("This class is a Singleton!")
    else:
      self.logger = LoggerFactory(self).getLogger()
      self.predictor = Predictor.from_path("libs/allennlp-conParser.tar.gz")
      ConParser.__instance = self

  def parse(self, sentence, save=True):
    # reset results
    if(save):
      self.results = None
      self.labels = None
      self.words = None
      self.tree = None
      self.tree_str = None
    
    results = self.predictor.predict(
      sentence=sentence
    )
    # save results
    labels = results['pos_tags']
    if(save):
      self.results = results
      self.labels = labels
      self.words = results['tokens']
      self.tree = results['hierplane_tree']['root']
      self.tree_str = results['trees']
    return labels

  def getPhrase(self, word='have', phraseType='VP'):
    if(word not in self.words):
      raise ValueError(f"Word:{word} is not in '{self.words}'")
    root = self.results['hierplane_tree']['root']
    # if(root['nodeType'] == phraseType and word == word_tokenize(root['word'])[0] ):
    if(root['nodeType'] == phraseType and word in word_tokenize(root['word']) ):
      return root
    child_list = root['children']
    # count = 0
    for node in child_list:
      # print(f"===== {count} =====")
      # print(type(node))
      # print(node)      
      if('children' in node.keys()):
        child_list.extend(node['children'])
      # count = count + 1
      # if(node['nodeType'] == phraseType and word == word_tokenize(node['word'])[0] ):
      if(node['nodeType'] == phraseType and word in word_tokenize(node['word']) ):
        return node

  def extractNounPhrase_WhPhrase(self,phrase):
    self.extract_noun = None
    pos = self.parse(phrase,save=False)
    # words = phrase
    words = word_tokenize(phrase)
    count = 0
    nounPhrase = []
    for w,p in zip(words,pos):
      count = count + 1
      # print(count, w, p)
      # if the first word is not How, we abort mission
      if(count == 1):
        if(w.lower() == "how"):
          continue
        else:
          raise ValueError(f"Phrase:{phrase} is not a 'how' phrases.")

      # check second word
      if(count == 2 and w.lower() == 'many')  :
        continue
        
      nounPhrase.append(w)
      if(p in ConParser.SET_LABEL_NOUN):
        self.extract_noun = w

    self.logger.debug(f"Extract NounPhrase:{nounPhrase} Noun:{self.extract_noun} from WhPhrase:{phrase}")
    return nounPhrase




""" Semantic Role Labeling Parser """
class SRLParser:
  __instance = None
  
  @staticmethod 
  def getInstance():
    if SRLParser.__instance == None:
        SRLParser()
    return SRLParser.__instance

  def __init__(self):
    if SRLParser.__instance != None:
        raise Exception("This class is a Singleton!")
    else:
        self.logger = LoggerFactory(self).getLogger()
        self.predictor = Predictor.from_path("libs/allennlp-SRL.tar.gz")
        SRLParser.__instance = self

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
    auxVerbs = []
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
      auxVerbs.append(target['verb'])
      tags[target['verb']] = tagged_words
      roles[target['verb']] = roles_set

    self.words = words
    self.verbs = verbs
    self.auxVerbs = auxVerbs
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
