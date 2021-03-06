from systems.LoggerFactory import LoggerFactory
from nltk.tokenize import sent_tokenize
from MSParser import ConParser,SRLParser
from MSCorpus import MSCorpus, WordSem
# from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import WordNetLemmatizer
from Entity import Entity
import json

class Question:
  TYPE_AddTo_ResultUnknow = 0
  TYPE_TakeFrom_ResultUnknow = 1
  TYPE_PutTogetherTakeApart_TotalUnknow = 2
  TYPE_Compare_BiggerUnknow = 3
  LIST_TYPE = {
    0 : "Add to - Result Unknown",
    1 : "Take from - Result Unknown",
    2 : "Put Together/Take Apart - Total Unknown",
    3 : "Compare - Bigger Unknown",
  }

  def __init__(self, question):
    self.logger = LoggerFactory(self).getLogger()
    if(question == ""): raise ValueError(f"question is an empty string")    

    self.question = question
    self.sentences = []
    self.problemType = None
    self.__construct__()
    self.__defineProblemType()
    self.logger.debug(f"question:{self}")

  @staticmethod
  def getProblemTypeName(enum):
    return Question.LIST_TYPE.get(enum, "Invalid numbner")

  def getQuerySentence(self):
    querySentences = [sent for index, sent in enumerate(self.sentences) if sent.type == Sentence.TYPE_QUERY]
    if(len(querySentences) != 1):
      raise ValueError(f"Too many query sentnce. Only expect 1 for now - {querySentences}")
    return querySentences[0]

  def getStatementSentences(self):
    statementSentences = [sent for index, sent in enumerate(self.sentences) if sent.type == Sentence.TYPE_STATEMENT]
    return statementSentences

  def __construct__(self):
    # 1. Split the string into sentences.
    sents = sent_tokenize(self.question)
    for index,sent in enumerate(sents):
      s = Sentence(index,sent)
      self.sentences.append( s )

  def __defineProblemType(self):
    """ Check if any of the sentences has comparison phrase """
    for sent in self.sentences:
      # compare phrase are more ... than, less ... than, and fewer ... than
      # more, less, fewer and followed by than
      try:
        than = sent.getWord('than')
      except:
        # There is no word 'than'
        continue
      
      try:
        more = sent.getWord('more')
        if(more.index < than.index):
          self.problemType = Question.TYPE_Compare_BiggerUnknow
          return        
      except:
        # There is no word 'more'
        pass

      try:
        less = sent.getWord('less')
        if(less.index < than.index):
          self.problemType = Question.TYPE_Compare_BiggerUnknow
          return     
      except:
        # There is no word 'less'
        pass

      try:
        fewer = sent.getWord('fewer')
        if(fewer.index < than.index):
          self.problemType = Question.TYPE_Compare_BiggerUnknow
          return
      except:
        # There is no word 'fewer'
        pass

    # DONE: Extract entity in each sentence \\(  >w<)// \(>___< .)// 
    for sent in self.sentences:
      actor = sent.getArg(0)
      entity = [w for w in sent.getArg(1) if ( w.name.lower() not in set({'how','many'}) ) ]
      sent.entity = Entity(entity)
      sent.actor = Entity(actor)

    query = self.getQuerySentence()
    # macthing entity
    query_entity = query.entity
    state_entities = [state.entity for state in self.getStatementSentences()]
    entity_matches = []
    for state_entity in state_entities:
      entity_matches.append(Entity.match(query_entity,state_entity))
    self.logger.debug(f"Entity Matches:{[Entity.getMatchName(r) for r in entity_matches]}")

    # matching actor
    query_actor = query.actor
    state_actors = [state.actor for state in self.getStatementSentences()]
    actor_mathces = []
    for state_actor in state_actors:
      actor_mathces.append(Entity.match(query_actor,state_actor))
    self.logger.debug(f"Actor Matches:{[Entity.getMatchName(r) for r in actor_mathces]}")

    if(Entity.MATCH_PARTIALLY in entity_matches):
      self.problemType = Question.TYPE_PutTogetherTakeApart_TotalUnknow
    if(Entity.MATCH_NO in actor_mathces):
      self.problemType = Question.TYPE_PutTogetherTakeApart_TotalUnknow
    
    if(self.problemType == None):
      self.problemType = Question.TYPE_AddTo_ResultUnknow

    # # get query sentence
    # querySentence = self.getQuerySentence()
    # # detecting sentence structure.
    # # Class 1: counting
    # # Structure: How many [object] {do} [someone] {verb - possession} [optional]
    # # Solution: These type of problem class ask us to count the number of object that someone acting on it. 
    # #           the counting must accounting for interchangeble verb list consume - eat and colour - paint.


    # verb = querySentence.getVerb()
    # ms = MSCorpus.getInstance()
    # self.problemType = ms.getWordSem(verb.lemma)

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    obj = {}
    obj["problemType"] = Question.getProblemTypeName(self.problemType)
    obj["question"] = self.question
    obj["sentencens"] = [json.loads(s.__str__()) for s in self.sentences]
    return json.dumps(obj)

# class QuestionTemplate:
#   def __init__(self):
#     self.logger = LoggerFactory(self).getLogger()
#     self.counting = Sentence(0,"How many object does someone verb")

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

  STRUCTURE_STA_THERE = 0
  STRUCTURE_STA_ARG1_PREP = 1
  STRUCTURE_STA_ARG0_VERB_ARG1 = 2

  STRUCTURE_QUE_THERE = 0
  STRUCTURE_QUE_ARG1_PREP = 1
  STRUCTURE_QUE_ARG0_VERB_ARG1 = 2

  LIST_STA_STRUCTURE = {
    0 : 'There {be} (ARG1) (PP)',
    1 : '(ARG1) {verb} {prep} (ARG2)',
    2 : '(ARG0) {verb} (ARG1)'
  }

  LIST_QUE_STRUCTURE = {
    0 : 'How many (ARG1) {be} there (PP)',
    1 : 'How many (ARG1) {be} {prep} (ARG2)',
    2 : 'How many (ARG1) {do} (ARG0) {verb}'
  }

  def __init__(self,index,sentence):
    self.logger = LoggerFactory(self).getLogger()
    if(sentence == ""): raise ValueError(f"Sentence is an empty string")

    self.index = index
    self.sentence = sentence
    self.type = Sentence.TYPE_STATEMENT
    self.tense = Sentence.TENSE_OTHERS
    self.structure = None
    self.verb = None
    self.ARG0 = []
    self.ARG1 = []
    self.ARG2 = []
    self.ARG3 = []
    self.ARG4 = []
    self.entity = Entity()
    self.actor = Entity()

    self.__parsePOS()
    # With POS, we can determine if the sentence is a query
    self.__checkType()
    self.__extractVerb()
    self.__checkTense()
    self.__parseSRL()
    self.__setSRLArgument()
    self.__setStructure()

  def getArg(self,num):
    validNum = set({0,1,2,3,4})
    if(num not in validNum): raise ValueError(f"{num} is not in {validNum}")
    target = f"ARG{num}"
    arg = [w for w in self.words if(w.SRLRole == target)]
    return arg

  def getStructureName(self,enum,type):
    if(type == Sentence.TYPE_STATEMENT):
      return Sentence.LIST_STA_STRUCTURE.get(enum, "Invalid number")
    elif(type == Sentence.TYPE_QUERY):
      return Sentence.LIST_QUE_STRUCTURE.get(enum, "Invalid number")
    else:
      raise ValueError(f"Invalid type={type}")

  def getTenseName(self,enum):
    return Sentence.LIST_TENSE.get(enum, "Invalid number")

  def getTypeName(self,enum):
    return Sentence.LIST_TYPE.get(enum, "Invalid number")

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
    raise ValueError(f"I don't know why. index={index}. word={self.words[index]}")

  def __setStructure(self):
    if(self.type == Sentence.TYPE_STATEMENT):
      # First word is 'There'
      firstWord = self.words[0]
      if(firstWord.lemma.lower() == 'there'):
        self.structure = Sentence.STRUCTURE_STA_THERE
      # First word is ARG1
      elif(firstWord.SRLRole == 'ARG1'):
        self.structure = Sentence.STRUCTURE_STA_ARG1_PREP
      # First word is ARG0
      elif(firstWord.SRLRole == 'ARG0'):
        self.structure = Sentence.STRUCTURE_STA_ARG0_VERB_ARG1
      else:
        raise ValueError(f"Non of the condition is met.")

    # elif(self.type  == Sentence.TYPE_QUERY):
    #   raise Exception(f"not yet implement")
    # else:
    #   raise Exception(f"type={self.type} is not yet implement")
    
    self.logger.debug(self.getStructureName(self.structure,self.type))

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
    self.logger.debug(f"{verbs} {auxVerbs}")
    set_auxVerbs = set(auxVerbs)
    self.logger.debug(f"SRL verb:{verbs}")
    obj = {"isExist": False, "index":None}
    self.do = obj.copy()
    self.have = obj.copy()
    self.verb = obj.copy()
    if(len(verbs) == 1):
      word = self.getWord(verbs[0])
      self.verb["isExist"] = True
      self.verb["index"] = word.index
      self.logger.debug(f"Found real_verb:{self.verb} | word:{word}")
      return None

    set_do = WordSem.SET_DO
    set_have = WordSem.SET_HAVE
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

    if(self.verb["isExist"] == False):
      index = 0
      # if we do exist, verbs[1] is real verb
      if(self.do["isExist"]): index = 1
      tmp = auxVerbs[index]
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
    obj["structure"] = self.getStructureName(self.structure,self.type)
    obj["type"] = self.getTypeName(self.type)
    obj["verb"] = self.verb
    obj["tense"] = self.getTenseName(self.tense)
    obj["ARG0"] = self.ARG0
    obj["ARG1"] = self.ARG1
    obj["ARG2"] = self.ARG2
    obj["ARG3"] = self.ARG3
    obj["ARG4"] = self.ARG4
    obj["entity"] = json.loads(self.entity.__str__())
    obj["actor"] = json.loads(self.actor.__str__())
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

  def isEqual(self,word):
    a = json.loads(self.__str__())
    b = json.loads(word.__str__())
    a.pop('index')
    b.pop('index')
    return a == b

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

# qt = QuestionTemplate()
# print(qt.counting)