from systems.LoggerFactory import LoggerFactory
from nltk.parse.corenlp import CoreNLPDependencyParser
from nltk.parse.corenlp import CoreNLPParser
from nltk.tree import ParentedTree
from nltk.tokenize import sent_tokenize
import nltk
from SRL import SRL
from ConParser import ConParser
from WordProcessor import WordProcessor

class Main:
  def __init__(self):
    self.logger = LoggerFactory(self).getLogger()

  def run(self):
    self.logger.debug('Starting...')
    self.logger.debug('Init ConParser')
    cParser = ConParser.getInstance()
    self.logger.debug('Init SRL')
    srl = SRL.getInstance()
    self.logger.debug('Run question')

    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples does Sam have?"
    question = "Sam has 5 apples. Sam eats 3 apples. How many apples does Sam eat?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples are in Sam's Stomach?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples are with Sam?"
    """ 
    1. Split the string into sentences.
    2. Usually, the last sentence is the query statement. Use that to identify problem class.
      2.1 Check the type of question (What, Where, When, Why, How).
      2.2 Extract verb.
      2.3 Use both information to identify problem class.
    3. Process each sentence according to the problem class.     
    """

    # 1. Split the string into sentences.
    sentences = sent_tokenize(question)
    self.logger.debug(f"question: {sentences}")

    # 2. Usually, the last sentence is the query statement. Use that to identify problem class.
    # find query statement
    pos_sentences = []
    wh_sentences = []
    for sent in sentences:
      pos_sent = cParser.parse(sent)
      pos_sentences.append(pos_sent)
      isWh = pos_sent[0] == "WRB"
      wh_sentences.append(isWh)
      self.logger.debug(f"sentence: {sent} | pos: {pos_sent} | isWh: {isWh}")

    # pos_sentences
    # >>> [['NNP', 'VBZ', 'CD', 'NNS', '.'], 
    #   ['NNP', 'VBZ', 'CD', 'NNS', '.'], 
    #   ['WRB', 'JJ', 'NNS', 'VBZ', 'NNP', 'VB', 'VBN', '.']]
    # wh_sentences
    # >>> [False, False, True]

    queryStatement = sentences[wh_sentences.index(True)]
    self.logger.debug(f"queryStatement: {queryStatement}")
    # 2.1 Check the type of question (What, Where, When, Why, How).
    pass

    # 2.2 Extract verb.
    verbs = srl.parse(queryStatement)
    self.logger.debug(f"verbs: {verbs}")
    self.logger.debug(f"SRL-Dump: {srl.results}")

    # 2.3 Use both information to identify problem class.


main = Main()
main.run()
# main.run()
