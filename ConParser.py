from systems.LoggerFactory import LoggerFactory
from allennlp.predictors.predictor import Predictor
from nltk.tokenize import word_tokenize

class ConParser:
  __instance = None
  
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
    
    results = self.predictor.predict(
      sentence=sentence
    )
    # save results
    if(save):
      self.results = results
      self.labels = results['pos_tags']
      self.words = results['tokens']
    return self.labels

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

# sent = "How many apples did Sam have?"
# sent = "How many apples did Sam have this breakfast?"
# sent = "How many apples does Sam have left?"
# sent = "How many black apples"
# cParser = ConParser.getInstance()
# pos = cParser.parse(sent)
# print(cParser.words)
# print(pos)
# print(cParser.results)
# output = cParser.extractNounPhrase_WhPhrase(sent)
# print(output)
# print(cParser.getPhrase('apples','NP'))

# pos = cParser.parse("How many apples does Sam eat?")
# words = cParser.words
# for w,p in zip(words,pos):
#   print(w,p)