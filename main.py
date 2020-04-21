from systems.LoggerFactory import LoggerFactory
from nltk.parse.corenlp import CoreNLPDependencyParser
from nltk.parse.corenlp import CoreNLPParser
from nltk.tree import ParentedTree
from nltk.tokenize import sent_tokenize
import nltk
from MSParser import ConParser, SRLParser

from WordProcessor import WordProcessor
from MSCorpus import MSCorpus, ProblemClass
from Solver import DeductiveSolver
from Question import Question

class Main:
  def __init__(self):
    
    self.logger = LoggerFactory(self).getLogger()

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
    ProblemClass.loadKnowledge(rollback=False)

  def loadQuestion(self):
    question = "Sam has 5 apples. Sam eats 3 apples. How many apples did Sam have?"
    question = "Sam had 5 apples this breakfast. Sam ate 3 apples. How many apples did Sam have?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples does Sam have left?"
    # question = "Sam has 5 apples. Sam eats 3 apples. Mark consumes 10 more apples. How many apples does Sam consume?"
    # question = "Sam has 5 apples. Sam eats 3 apples. Sam eats 10 more apples. How many apples does Sam eat?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples are in Sam's Stomach?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples are with Sam?"
    return question

  def run(self):
    self.loadModule()
    cParser = self.cParser 
    srl = self.srl
    wp = self.wp
    msc = self.msc

    # 1. Constract & Break question into sentence and word
    question = Question(self.loadQuestion())
    """ 
    1. Split the string into sentences.
    2. Usually, the last sentence is the query statement. Use that to identify problem class.
      2.a Check the type of question (What, Where, When, Why, How).
      2.a-1 Deciding have
      2.b Extract verb.
      2.c Use both information to identify problem class.
    3. Process each sentence according to the problem class.     
    """
    # sentences = sent_tokenize(question)
    # self.logger.debug(f"question:{sentences}")
# question:[
# {"index": 0, "sentence": "Sam has 5 apples.", "type": "STATEMENT", 
#   "verb": {"isExist": true, "index": 1}, "ARG0": [0], "ARG1": [2, 3], 
#   "tree": "(S (NP (NNP Sam)) (VP (VBZ has) (NP (CD 5) (NNS apples))) (. .))", 
#   "words": [
#     {"index": 0, "name": "Sam", "lemma": "Sam", "pos": "NNP", "SRL": {"tag": "B-ARG0", "suffix": "B", "role": "ARG0"}}, 
#     {"index": 1, "name": "has", "lemma": "have", "pos": "VBZ", "SRL": {"tag": "B-V", "suffix": "B", "role": "V"}}, 
#     {"index": 2, "name": "5", "lemma": "5", "pos": "CD", "SRL": {"tag": "B-ARG1", "suffix": "B", "role": "ARG1"}}, 
#     {"index": 3, "name": "apples", "lemma": "apple", "pos": "NNS", "SRL": {"tag": "I-ARG1", "suffix": "I", "role": "ARG1"}}, 
#     {"index": 4, "name": ".", "lemma": ".", "pos": ".", "SRL": {"tag": "O", "suffix": "", "role": "O"}}]}, 
# {"index": 1, "sentence": "Sam eats 3 apples.", "type": "STATEMENT", 
#   "verb": {"isExist": true, "index": 1}, "ARG0": [0], "ARG1": [2, 3], 
#   "tree": "(S (NP (NNP Sam)) (VP (VBZ eats) (NP (CD 3) (NNS apples))) (. .))", 
#   "words": [
#     {"index": 0, "name": "Sam", "lemma": "Sam", "pos": "NNP", "SRL": {"tag": "B-ARG0", "suffix": "B", "role": "ARG0"}}, 
#     {"index": 1, "name": "eats", "lemma": "eat", "pos": "VBZ", "SRL": {"tag": "B-V", "suffix": "B", "role": "V"}}, 
#     {"index": 2, "name": "3", "lemma": "3", "pos": "CD", "SRL": {"tag": "B-ARG1", "suffix": "B", "role": "ARG1"}}, 
#     {"index": 3, "name": "apples", "lemma": "apple", "pos": "NNS", "SRL": {"tag": "I-ARG1", "suffix": "I", "role": "ARG1"}}, 
#     {"index": 4, "name": ".", "lemma": ".", "pos": ".", "SRL": {"tag": "O", "suffix": "", "role": "O"}}]}, 
# {"index": 2, "sentence": "How many apples did Sam have?", "type": "QUERY", 
#   "verb": {"isExist": true, "index": 5}, "ARG0": [4], "ARG1": [], 
#   "tree": "(SBARQ (WHNP (WRB How) (JJ many) (NNS apples)) (SQ (VBD did) (NP (NNP Sam)) (VP (VB have))) (. ?))", 
#   "words": [
#     {"index": 0, "name": "How", "lemma": "How", "pos": "WRB", "SRL": {"tag": "B-ARG1", "suffix": "B", "role": "ARG1"}}, 
#     {"index": 1, "name": "many", "lemma": "many", "pos": "JJ", "SRL": {"tag": "I-ARG1", "suffix": "I", "role": "ARG1"}}, 
#     {"index": 2, "name": "apples", "lemma": "apple", "pos": "NNS", "SRL": {"tag": "I-ARG1", "suffix": "I", "role": "ARG1"}}, 
#     {"index": 3, "name": "did", "lemma": "do", "pos": "VBD", "SRL": {"tag": "O", "suffix": "", "role": "O"}}, 
#     {"index": 4, "name": "Sam", "lemma": "Sam", "pos": "NNP", "SRL": {"tag": "B-ARG0", "suffix": "B", "role": "ARG0"}}, 
#     {"index": 5, "name": "have", "lemma": "have", "pos": "VB", "SRL": {"tag": "B-V", "suffix": "B", "role": "V"}}, 
#     {"index": 6, "name": "?", "lemma": "?", "pos": ".", "SRL": {"tag": "O", "suffix": "", "role": "O"}}]}]

    
main = Main()
main.run()
# main.run()