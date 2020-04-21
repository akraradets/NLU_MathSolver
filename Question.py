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


  def __repr__(self):
    return self.__str__()

  def __str__(self):
    obj = {}
    obj["question"] = self.question
    obj["sentencens"] = [json.loads(s.__str__()) for s in self.sentences]
    return json.dumps(obj)



class Sentence:
  # Tense
  TENSE_OTHERS = 0
  TENSE_PRESENT_SIMPLE = 1
  LIST_TENSE = {
    0 : 'OTHERS',
    1 : 'PRESENT_SIMPLE'
  }
  # Sentence Type
  TYPE_STATEMENT = 0
  TYPE_QUERY = 1
  LIST_TYPE = {
      0 : 'STATEMENT',
      1 : 'QUERY'
    }

  def __init__(self,index,sentence):
    self.logger = LoggerFactory(self).getLogger()
    if(sentence == ""): raise ValueError(f"Sentence is an empty string")

    self.index = index
    self.sentence = sentence
    self.type = Sentence.TYPE_STATEMENT
    self.tense = Sentence.TENSE_OTHERS
    self.verb = None
    self.ARG0 = []
    self.ARG1 = []
    self.ARG2 = []
    self.ARG3 = []
    self.ARG4 = []

    self.__parsePOS()
    # With POS, we can determine if the sentence is a query
    self.__checkType()
    self.__extractVerb()
    self.__checkTense()
    self.__parseSRL()
    self.__setSRLArgument()

  def getTenseName(self,enum):
    return Sentence.LIST_TENSE.get(enum, "Invalid numbner")

  def getTypeName(self,enum):
    return Sentence.LIST_TYPE.get(enum, "Invalid numbner")

  def getVerb(self):
    if(self.verb is None): raise ValueError(f"__extractVerb first")
    index_verb = self.verb["index"]
    return self.getWordBy(index=index_verb)

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
    """ Update Tag in words """
    verb = self.getVerb()
    for index, (w_my, w_srl, tag_srl) in enumerate(zip(self.words, srl.words, srl.tags[verb.name])):
      # w_my| [{"index": 0, "name": "How", "lemma": "How", "pos": "WRB"}, 
      #         {"index": 1, "name": "many", "lemma": "many", "pos": "JJ"}, 
      #         {"index": 2, "name": "apples", "lemma": "apple", "pos": "NNS"}, 
      #         {"index": 3, "name": "did", "lemma": "do", "pos": "VBD"}, 
      #         {"index": 4, "name": "Sam", "lemma": "Sam", "pos": "NNP"}, 
      #         {"index": 5, "name": "have", "lemma": "have", "pos": "VB"}, 
      #         {"index": 6, "name": "?", "lemma": "?", "pos": "."}]
      # w_srl| ['How', 'many', 'apples', 'did', 'Sam', 'have', '?']
      # tags| [{'word': 'How', 'tag': 'B-ARG1', 'suffix': 'B', 'role': 'ARG1'}, 
      #         {'word': 'many', 'tag': 'I-ARG1', 'suffix': 'I', 'role': 'ARG1'}, 
      #         {'word': 'apples', 'tag': 'I-ARG1', 'suffix': 'I', 'role': 'ARG1'}, 
      #         {'word': 'did', 'tag': 'O', 'suffix': '', 'role': 'O'}, 
      #         {'word': 'Sam', 'tag': 'B-ARG0', 'suffix': 'B', 'role': 'ARG0'}, 
      #         {'word': 'have', 'tag': 'B-V', 'suffix': 'B', 'role': 'V'}, 
      #         {'word': '?', 'tag': 'O', 'suffix': '', 'role': 'O'}]
      # check if the word is the same word. Just to be safe
      if(w_my.name != w_srl):
        raise ValueError(f"Array differ from sentence:{self.__getWordsAsArray} and SRL:{srl.words}")
      SRLTag = tag_srl['tag']
      suffix = tag_srl['suffix']
      role = tag_srl['role']
      w_my.setSRLTag(tag=SRLTag, suffix=suffix, role=role)

  def __setSRLArgument(self):
    for w in self.words:
      if(w.SRLRole == "ARG0"): self.ARG0.append(w.index)
      if(w.SRLRole == "ARG1"): self.ARG1.append(w.index)
      if(w.SRLRole == "ARG2"): self.ARG2.append(w.index)
      if(w.SRLRole == "ARG3"): self.ARG3.append(w.index)
      if(w.SRLRole == "ARG4"): self.ARG4.append(w.index)

  def __extractVerb(self):
    """ SRL Parse: Help us extract verb."""
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
        # have is real verb
        word = self.getWordBy(index=self.have["index"])
        self.verb["isExist"] = True
        self.verb["index"] = word.index
        # reset have
        self.have = obj.copy()
        self.logger.debug(f"Found real_verb:{self.verb} | word:{word}")

    # If there is no do and have, verbs will only have 1 verb.
    if(self.do["isExist"] == False and self.have["isExist"] == False):
      tmp = verbs[0]
      word = self.getWord(tmp)
      self.verb["isExist"] = True
      self.verb["index"] = word.index
      self.logger.debug(f"Found real_verb:{self.verb} | word:{word}")

  def __checkTense(self):
    """ Once we extract verb. We get the information of verbs and aux in the sentence. 
      If 'do' exist, it will be used to determine the tense of the sentence (past,present).
    """
    if(self.verb == None): raise ValueError(f"__extractVerb first")

    pos_present = set({"VB","VBZ"})
    # detect present simple tense
    # print(f"========|| {}   {self.getWordBy(index=self.do["index"])}")
    if( (self.do["isExist"] and self.getWordBy(index=self.do["index"]).pos in pos_present)
    or (self.do["isExist"] == False and self.getVerb().pos in pos_present) ):
      self.tense = Sentence.TENSE_PRESENT_SIMPLE
      self.logger.debug(f"This sentence is {self.getTenseName(self.tense)}")
      pass
    else:
      pass

  def __checkType(self):
    if(self.words is None): raise ValueError(f"__parsePOS first")
    # Check the first word if it is has a pos of WRB
    if(self.words[0].pos in ConParser.SET_LABEL_QUERY):
      self.type = Sentence.TYPE_QUERY

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
    obj["verb"] = self.verb
    obj["tense"] = self.getTenseName(self.tense)
    obj["ARG0"] = self.ARG0
    obj["ARG1"] = self.ARG1
    obj["ARG2"] = self.ARG2
    obj["ARG3"] = self.ARG3
    obj["ARG4"] = self.ARG4
    obj["tree"] = self.tree_str
    obj["words"] = self.__getWordsAsArray()
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
    self.SRLtag = ""
    self.SRLSuffix = ""
    self.SRLRole = ""
  
  def setSRLTag(self,tag,suffix,role):
    self.SRLtag = tag
    self.SRLSuffix = suffix
    self.SRLRole = role

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
    obj["SRL"] = {'tag':self.SRLtag, 'suffix':self.SRLSuffix, 'role':self.SRLRole}
    return json.dumps(obj)