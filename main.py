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
    sentences = sent_tokenize(question)
    self.logger.debug(f"question:{sentences}")


    
main = Main()
main.run()
# main.run()