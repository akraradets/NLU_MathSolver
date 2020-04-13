from systems.LoggerFactory import LoggerFactory
from nltk.parse.corenlp import CoreNLPDependencyParser
from nltk.parse.corenlp import CoreNLPParser
from nltk.tree import ParentedTree
from nltk.tokenize import sent_tokenize
import nltk
import SRL

class Main:
  def __init__(self):
    self.logger = LoggerFactory(self).getLogger()

  def run(self):
    self.logger.debug('Starting...')
    question = "Sam has 5 apples. Sam eats 3 apples. How many apples does Sam have left?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples does Sam eat?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples are in Sam's Stomach?"
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
    # print(sentences)


main = Main()
main.run()
# main.run()
