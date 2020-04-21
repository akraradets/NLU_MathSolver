from systems.LoggerFactory import LoggerFactory
from nltk.tokenize import sent_tokenize
from MSParser import ConParser,SRLParser
from MSCorpus import ProblemClass
# from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import WordNetLemmatizer 
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


  def __repr__(self):
    return self.__str__()
    
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
    self.type = Sentence.STATEMENT
    self.verb = None
    self.__parsePOS()
    # With POS, we can determine if the sentence is a query
    self.__checkType()
    self.__extractVerb()
    self.__parseSRL()

  def getTypeName(self,enum):
    return Sentence.LIST_TYPE.get(enum, "Invalid numbner")

  def getWord(self,word):
    if(self.words is None): raise ValueError(f"__parsePOS first")
    for w in self.words:
      if(w.name == word):
        return w
    raise NameError(f"word:{word} is not exist in {self.__getWordsAsArray()}")

  def getWordBy(self,index=None):
    if(self.words is None): raise ValueError(f"__parsePOS first")
    if(index != None): return self.words[index]
    raise ValueError(f"I don't know why")

  def __parsePOS(self):
    """ Con Parse: We get parseTree, POS, words """
    cParser = ConParser.getInstance()
    cParser.parse(self.sentence)
    self.words = []
    for index, (w, p) in enumerate( zip(cParser.words, cParser.labels) ):
      o = Word(index,w,p)
      self.words.append(o)

    self.tree = cParser.tree
    self.tree_str = cParser.tree_str
    self.logger.debug(f"{self}")

  def __parseSRL(self):
    if(self.verb == None): raise ValueError(f"__extractVerb first")
    """ SRL Parse: parse it with role """
    srl = SRLParser.getInstance()
    srl.parse(self.sentence)
    # arg1_phrase = srl.getRole('ARG1',target_verb)
    pass

  def __extractVerb(self):
    """ SRL Parse: Help us extract verb """
    srl = SRLParser.getInstance()
    verbs = srl.parse(self.sentence)
    auxVerbs = srl.auxVerbs
    set_auxVerbs = set(auxVerbs)

    obj = {"isExist": False, "index":None}
    self.do = obj.copy()
    self.have = obj.copy()
    self.verb = obj.copy()

    set_do = ProblemClass.SET_DO
    set_have = ProblemClass.SET_HAVE
    set_label_verb = ConParser.SET_LABEL_VERB
    words = self.words
    if(set_do.isdisjoint(set_auxVerbs) == False):
      tmp = set_do.intersection(set_auxVerbs).pop()
      word = self.getWord(tmp)
      self.do["isExist"] = True
      self.do["index"] = word.index
      self.logger.debug(f"Found do:{self.do} | word:{word}")
    if(set_have.isdisjoint(set_auxVerbs) == False):
      # if have is real verb or an aux?
      tmp = set_have.intersection(set_auxVerbs).pop()
      word = self.getWord(tmp)
      self.have["isExist"] = True
      self.have["index"] = word.index
      self.logger.debug(f"Found have:{self.have} | word:{word}")

      if(words[self.have["index"] + 1].pos in set_label_verb ):
        # The follow of have is a verb. Therefore, have is an aux and the follow word is the real verb
        word = self.getWordBy(index=self.have["index"] + 1)
        self.verb["isExist"] = True
        self.verb["index"] = word.index
        self.logger.debug(f"Found real_verb:{self.verb} | word:{word}")
      else:
        word = self.getWordBy(index=self.have["index"])
        self.verb["isExist"] = True
        self.verb["index"] = word.index
        self.logger.debug(f"Found real_verb:{self.verb} | word:{word}")

    # If there is no do and have, verbs will only have 1 verb.
    if(self.do["isExist"] == False and self.have["isExist"] == False):
      tmp = verbs[0]
      word = self.getWord(tmp)
      self.verb["isExist"] = True
      self.verb["index"] = word.index
      self.logger.debug(f"Found real_verb:{self.verb} | word:{word}")


  def __checkType(self):
    if(self.words is None): raise ValueError(f"__parsePOS first")
    # Check the first word if it is has a pos of WRB
    if(self.words[0].pos in ConParser.SET_LABEL_QUERY):
      self.type = Sentence.QUERY

  def __getWordsAsArray(self):
    if(self.words is None): raise ValueError(f"__parsePOS first")
    words = [json.loads(w.__str__()) for w in self.words]
    return words

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    obj = {}
    obj["index"] = self.index
    obj["sentence"] = self.sentence
    obj["type"] = self.getTypeName(self.type)
    obj["tree"] = self.tree_str
    obj["words"] = self.__getWordsAsArray()
    obj["verb"] = self.verb
    return json.dumps(obj)



class Word:
  def __init__(self,index,word,pos):
    self.logger = LoggerFactory(self).getLogger()
    if(word == ""): raise ValueError(f"Word is an empty string")
    if(pos == ""):  raise ValueError(f"POS is an empty string")
    self.index = index
    self.name = word
    self.pos = pos
    self.lemma = word
    self.__setLemma()
  
  def __setLemma(self):
    lemmatizer = WordNetLemmatizer()
    if(self.pos in ConParser.SET_LABEL_VERB):
      self.lemma = lemmatizer.lemmatize(self.name,'v')
    elif(self.pos in ConParser.SET_LABEL_NOUN):
      self.lemma = lemmatizer.lemmatize(self.name,'n')

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    obj = {}
    obj["index"] = self.index
    obj["name"] = self.name
    obj["lemma"] = self.lemma
    obj["pos"] = self.pos
    return json.dumps(obj)