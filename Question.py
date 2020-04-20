from systems.LoggerFactory import LoggerFactory
from nltk.tokenize import sent_tokenize
from MSParser import ConParser,SRLParser
import json

class Question:
  def __init__(self, question):
    self.logger = LoggerFactory(self).getLogger()
    if(question == ""): raise ValueError(f"question is an empty string")    

    self.question = question
    self.sentences = []
    self.__construct__()

  def __construct__(self):
    # 1. Split the string into sentences.
    sents = sent_tokenize(self.question)
    for index,sent in enumerate(sents):
      s = Sentence(index,sent)
      self.sentences.append( s )

    self.logger.debug(f"question:{self.sentences}")
    print(self)

  def __str__(self):
    obj = {}
    obj["question"] = self.question
    obj["sentencens"] = [json.loads(s.__str__()) for s in self.sentences]
    return json.dumps(obj)



class Sentence:
  STATEMENT = 0
  QUERY = 1
  LIST_TYPE = {
      0 : 'STATEMENT',
      1 : 'QUERY'
    }

  def __init__(self,index,sentence):
    self.logger = LoggerFactory(self).getLogger()
    if(sentence == ""): raise ValueError(f"Sentence is an empty string")

    self.index = index
    self.sentence = sentence
    self.type = -1
    self.__parse()

  def getTypeName(self,enum):
    return Sentence.LIST_TYPE.get(enum, "Invalid numbner")

  def __parse(self):
    """ Con Parse: We get parseTree, POS, words """
    cParser = ConParser.getInstance()
    cParser.parse(self.sentence)
    self.words = []
    for index, (w, p) in enumerate( zip(cParser.words, cParser.labels) ):
      o = Word(index,w,p)
      self.words.append(o)

    self.tree = cParser.tree
    self.tree_str = cParser.tree_str

    """ SRL Parse: We get semantic Role """
    # srl = SRLParser.getInstance()
    # verbs = srl.parse()


  def __str__(self):
    obj = {}
    obj["index"] = self.index
    obj["sentence"] = self.sentence
    obj["type"] = self.getTypeName(self.type)
    obj["tree"] = self.tree_str
    obj["words"] = [json.loads(w.__str__()) for w in self.words]
    return json.dumps(obj)



class Word:
  def __init__(self,index,word,pos):
    self.logger = LoggerFactory(self).getLogger()
    if(word == ""): raise ValueError(f"Word is an empty string")
    if(pos == ""):  raise ValueError(f"POS is an empty string")
    self.index = index
    self.name = word
    self.pos = pos
  
  def __str__(self):
    obj = {}
    obj["index"] = self.index
    obj["name"] = self.name
    obj["pos"] = self.pos
    return json.dumps(obj)