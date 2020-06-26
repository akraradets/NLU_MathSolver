from systems.LoggerFactory import LoggerFactory
# from nltk.parse.corenlp import CoreNLPDependencyParser
# from nltk.parse.corenlp import CoreNLPParser
# from nltk.tree import ParentedTree
from nltk.tokenize import sent_tokenize
import nltk
from MSParser import ConParser, SRLParser

from WordProcessor import WordProcessor
from MSCorpus import MSCorpus, WordSem
from Solver import PossessiveSolver
from Question import Question
from Equation import Equation
from Entity import Entity
import json

class Main:
  def __init__(self):
    
    self.logger = LoggerFactory(self).getLogger()
    self.loadModule()

  def loadModule(self):
    self.logger.debug('Init ConParser')
    self.cParser = ConParser.getInstance()
    self.logger.debug('Init SRL')
    self.srl = SRLParser.getInstance()
    self.logger.debug('Init WordProcessor')
    self.wp = WordProcessor.getInstance()
    self.logger.debug('Init MSCorpus')
    self.msc = MSCorpus.getInstance()
    self.logger.debug('Load KnowledgeBase')
    WordSem.loadKnowledge(rollback=False)

  def run(self):
    dataset = self.loadQuestion()
    for data in dataset:
      print(f"================ Question-{data['No.']} ================")
      question = Question(data['Question'])
      problemTypeName = Question.getProblemTypeName(question.problemType)
      if(problemTypeName != data["Type"]):
        self.logger.info(f"{data['No.']} is ***incorrect***.|Type:{problemTypeName}|Correct:{data['Type']}")  
        break
      else:
          self.logger.info(f"{data['No.']} is correct|Type:{problemTypeName}|Correct:{data['Type']}")
      # equation = self.solve(question)
      # self.logger.debug(f"Equation:{equation.prettify()}|Dump:{equation}")
      # answer = equation.evalute()
      # if(answer != data['Answer']):
      #   self.logger.info(f"{data['No.']} is ***incorrect***.|Answer:{answer}|Correct:{data['Answer']}")
      #   break
      # else:
      #   self.logger.info(f"{data['No.']} is correct|Answer:{answer}|Correct:{data['Answer']}")
    # 1. Constract & Break question into sentence and word
    # question = Question(self.loadQuestion())
    # self.solve(question)

  def loadQuestion(self):
    filename = "Dataset/dataset_commoncore_selected.json"
    with open(filename, 'r') as stream:
      dataset = json.loads(stream.read())
    # print(dataset_json)
    # question = "Sam has 5 red delicious apples. Sam eats 3 black apples. How many apples does Sam have?"
    # question = "Sue eats 3 ear of corn. Sue eats 1 more corn. How many corn does Sue eat"
    # question = "Sam had 5 apples this breakfast. Sam ate 3 apples. How many apples did Sam have?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples does Sam have left?"
    # question = "Sam has 5 apples. Sam eats 3 apples. Mark consumes 10 more apples. How many apples does Sam consume?"
    # question = "Sam has 5 apples. Sam eats 3 apples. Sam eats 10 more apples. How many apples does Sam have?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples are in Sam's Stomach?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples are with Sam?"

    return dataset


  def solve(self,question):
    cParser = self.cParser 
    srl = self.srl
    wp = self.wp
    msc = self.msc
    
    # The question will be constructed as follow
    # [{"index": 0, "sentence": "Sam has 5 apples.", "type": "STATEMENT", 
    #   "verb": {"isExist": true, "index": 1}, "tense": "PRESENT_SIMPLE", "ARG0": [0], "ARG1": [2, 3], "ARG2": [], "ARG3": [], "ARG4": [], 
    #   "tree": "(S (NP (NNP Sam)) (VP (VBZ has) (NP (CD 5) (NNS apples))) (. .))", 
    #   "words": [
    #     {"index": 0, "name": "Sam", "lemma": "Sam", "pos": "NNP", "SRL": {"tag": "B-ARG0", "suffix": "B", "role": "ARG0"}}, 
    #     {"index": 1, "name": "has", "lemma": "have", "pos": "VBZ", "SRL": {"tag": "B-V", "suffix": "B", "role": "V"}}, 
    #     {"index": 2, "name": "5", "lemma": "5", "pos": "CD", "SRL": {"tag": "B-ARG1", "suffix": "B", "role": "ARG1"}}, 
    #     {"index": 3, "name": "apples", "lemma": "apple", "pos": "NNS", "SRL": {"tag": "I-ARG1", "suffix": "I", "role": "ARG1"}}, 
    #     {"index": 4, "name": ".", "lemma": ".", "pos": ".", "SRL": {"tag": "O", "suffix": "", "role": "O"}}]}, 
    # {"index": 1, "sentence": "Sam eats 3 apples.", "type": "STATEMENT", 
    #   "verb": {"isExist": true, "index": 1}, "tense": "PRESENT_SIMPLE", "ARG0": [0], "ARG1": [2, 3], "ARG2": [], "ARG3": [], "ARG4": [], 
    #   "tree": "(S (NP (NNP Sam)) (VP (VBZ eats) (NP (CD 3) (NNS apples))) (. .))", 
    #   "words": [
    #     {"index": 0, "name": "Sam", "lemma": "Sam", "pos": "NNP", "SRL": {"tag": "B-ARG0", "suffix": "B", "role": "ARG0"}}, 
    #     {"index": 1, "name": "eats", "lemma": "eat", "pos": "VBZ", "SRL": {"tag": "B-V", "suffix": "B", "role": "V"}}, 
    #     {"index": 2, "name": "3", "lemma": "3", "pos": "CD", "SRL": {"tag": "B-ARG1", "suffix": "B", "role": "ARG1"}}, 
    #     {"index": 3, "name": "apples", "lemma": "apple", "pos": "NNS", "SRL": {"tag": "I-ARG1", "suffix": "I", "role": "ARG1"}}, 
    #     {"index": 4, "name": ".", "lemma": ".", "pos": ".", "SRL": {"tag": "O", "suffix": "", "role": "O"}}]}, 
    # {"index": 2, "sentence": "How many apples does Sam have?", "type": "QUERY", 
    #   "verb": {"isExist": true, "index": 5}, "tense": "PRESENT_SIMPLE", "ARG0": [4], "ARG1": [0, 1, 2], "ARG2": [], "ARG3": [], "ARG4": [], 
    #   "tree": "(SBARQ (WHNP (WRB How) (JJ many) (NNS apples)) (SQ (VBZ does) (NP (NNP Sam)) (VP (VB have))) (. ?))", 
    #   "words": [
    #     {"index": 0, "name": "How", "lemma": "How", "pos": "WRB", "SRL": {"tag": "B-ARG1", "suffix": "B", "role": "ARG1"}}, 
    #     {"index": 1, "name": "many", "lemma": "many", "pos": "JJ", "SRL": {"tag": "I-ARG1", "suffix": "I", "role": "ARG1"}}, 
    #     {"index": 2, "name": "apples", "lemma": "apple", "pos": "NNS", "SRL": {"tag": "I-ARG1", "suffix": "I", "role": "ARG1"}}, 
    #     {"index": 3, "name": "does", "lemma": "do", "pos": "VBZ", "SRL": {"tag": "O", "suffix": "", "role": "O"}}, 
    #     {"index": 4, "name": "Sam", "lemma": "Sam", "pos": "NNP", "SRL": {"tag": "B-ARG0", "suffix": "B", "role": "ARG0"}}, 
    #     {"index": 5, "name": "have", "lemma": "have", "pos": "VB", "SRL": {"tag": "B-V", "suffix": "B", "role": "V"}}, 
    #     {"index": 6, "name": "?", "lemma": "?", "pos": ".", "SRL": {"tag": "O", "suffix": "", "role": "O"}}]}]
    
    # Tagging Question Type
    equation = Equation()
    if(question.problemClass == WordSem.DEDUCTIVE):
      # Deductive - counting number of entity due to the target action
      self.logger.debug(f"Calling deductiveSolver")
      query = question.getQuerySentence()
      query_actor = self.buildObj(query.getArg(0))
      query_entity = [w for w in query.getArg(1) if ( w.name.lower() not in set({'how','many'}) ) ]
      query_entity = self.buildObj(query_entity)
      query_action = query.getVerb()
      self.logger.debug(f"Query-Extract|action:{query_action.lemma}|actor:{query_actor}|entity:{query_entity}")
      statements = question.getStatementSentences()
      for statement in statements:
        state_actor = self.buildObj(statement.getArg(0))
        state_entity = self.buildObj(statement.getArg(1))
        state_action = statement.getVerb()
        self.logger.debug(f"{statement.index}-Extract|action:{state_action.lemma}|actor:{state_actor}|entity:{state_entity}")
        sameActor = self.compareObj(query_actor,state_actor)
        sameEntity = self.compareObj(query_entity,state_entity, partial=True)
        sameAction = wp.isSimilar(query_action.lemma, state_action.lemma, 'v') and msc.getWordSem(state_action.lemma) == WordSem.DEDUCTIVE
        self.logger.debug(f"{statement.index}-Compare|action:{sameAction}|actor:{sameActor}|entity:{sameEntity}")
        if(sameActor and sameAction and sameEntity):
          equation.add(state_entity['quantity'])

    elif(question.problemClass == WordSem.POSSESSIVE):
      self.logger.debug(f"Calling possessiveSolver")
      ps = PossessiveSolver()
      equation = ps.process(question)
      # query = question.getQuerySentence()
      # query_actor = self.buildObj(query.getArg(0))
      # print(f"================ {query.getArg(0)}")
      # query_entity = [w for w in query.getArg(1) if ( w.name.lower() not in set({'how','many'}) ) ]
      # query_entity = self.buildObj(query_entity)
      # query_action = query.getVerb()
      # self.logger.debug(f"Query-Extract|action:{query_action.lemma}|actor:{query_actor}|entity:{query_entity}")
      # statements = question.getStatementSentences()
      # for statement in statements:
      #   state_actor = self.buildObj(statement.getArg(0))
      #   state_entity = self.buildObj(statement.getArg(1))
      #   state_action = statement.getVerb()
      #   self.logger.debug(f"{statement.index}-Extract|action:{state_action.lemma}|actor:{state_actor}|entity:{state_entity}")
      #   sameActor = self.compareObj(query_actor,state_actor)
      #   sameEntity = self.compareObj(query_entity,state_entity, partial=True)
      #   actionClass = msc.getWordSem(state_action.lemma)
      #   self.logger.debug(f"{statement.index}-Compare|action:{WordSem.getName(actionClass)}|actor:{sameActor}|entity:{sameEntity}")
      #   if(state_action.lemma == 'have'):
      #     equation.add(state_entity['quantity'])       
      #   elif(actionClass == WordSem.DEDUCTIVE):
      #     equation.minus(state_entity['quantity'])

    else:
      raise f"The question does not set 'ProblemType'"
    return equation

  def compareObj(self,o1,o2,partial=False):
    c1 = o1['name'] == o2['name']
    c2 = None
    if(partial):
      c2 = o1['adjective'].isdisjoint(o2['adjective'])
    else:
      c2 = o1['adjective'] == o2['adjective']
    return c1 and c2

  def buildObj(self,wordArray):
    obj = {}
    obj['quantity'] = None
    obj['adjective'] = set()
    obj['name'] = None
    for w in wordArray:
      if(w.pos == 'CD'): obj['quantity'] = w.name
      if(w.pos == 'JJ'): obj['adjective'].add(w.name.lower())
      if(w.pos in ConParser.SET_LABEL_NOUN): obj['name'] = w.lemma.lower()
    return obj

main = Main()
main.run()