from systems.LoggerFactory import LoggerFactory
from allennlp.predictors.predictor import Predictor
from nltk.tokenize import word_tokenize

class ConParser:
  __instance = None
  
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

  def parse(self, sentence):
    # reset results
    self.results = None
    self.labels = None
    self.words = None
    
    results = self.predictor.predict(
      sentence=sentence
    )
    # save results
    self.results = results
    self.labels = results['pos_tags']
    self.words = results['tokens']
    return self.labels

  def getPhrase(self, word='have', phraseType='VP'):
    if(word not in self.words):
      raise ValueError(f"Word:{word} is not in '{self.words}'")
    root = self.results['hierplane_tree']['root']
    if(root['nodeType'] == phraseType and word == word_tokenize(root['word'])[0] ):
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
      if(node['nodeType'] == phraseType and word == word_tokenize(node['word'])[0] ):
        return node

# sent = "How many apples did Sam have?"
# sent = "How many apples did Sam have this breakfast?"
# sent = "How many apples does Sam have left?"

# cParser = ConParser.getInstance()
# pos = cParser.parse(sent)
# print(cParser.words)
# print(pos)
# print(cParser.getPhrase('have'))

# pos = cParser.parse("How many apples does Sam eat?")
# words = cParser.words
# for w,p in zip(words,pos):
#   print(w,p)