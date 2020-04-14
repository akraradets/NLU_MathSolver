from systems.LoggerFactory import LoggerFactory
from nltk.parse.corenlp import CoreNLPDependencyParser
from nltk.parse.corenlp import CoreNLPParser
from nltk.tree import ParentedTree
from nltk.tokenize import sent_tokenize
import nltk
from SRL import SRL
from ConParser import ConParser
from WordProcessor import WordProcessor
from MSCorpus import MSCorpus, ProblemClass

class Main:
  def __init__(self):
    self.logger = LoggerFactory(self).getLogger()

  def run(self):
    self.logger.debug('Starting...')
    self.logger.debug('Init ConParser')
    cParser = ConParser.getInstance()
    self.logger.debug('Init SRL')
    srl = SRL.getInstance()
    self.logger.debug('Init WordProcessor')
    wp = WordProcessor.getInstance()
    self.logger.debug('Init MSCorpus')
    msc = MSCorpus.getInstance()
    self.logger.debug('Run question')

    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples does Sam have?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples does Sam have left?"
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
    self.logger.debug(f"question:{sentences}")

    # 2. Usually, the last sentence is the query statement. Use that to identify problem class.
    # find query statement
    pos_sentences = []
    wh_sentences = []
    for sent in sentences:
      pos_sent = cParser.parse(sent)
      pos_sentences.append(pos_sent)
      isWh = pos_sent[0] == "WRB"
      wh_sentences.append(isWh)
      self.logger.debug(f"sentence:{sent}|pos:{pos_sent}|isWh:{isWh}")

    # pos_sentences
    # >>> [['NNP', 'VBZ', 'CD', 'NNS', '.'], 
    #   ['NNP', 'VBZ', 'CD', 'NNS', '.'], 
    #   ['WRB', 'JJ', 'NNS', 'VBZ', 'NNP', 'VB', 'VBN', '.']]
    # wh_sentences
    # >>> [False, False, True]

    queryStatement = sentences[wh_sentences.index(True)]
    self.logger.debug(f"queryStatement:{queryStatement}")
    # 2.1 Check the type of question (What, Where, When, Why, How).
    pass

    # 2.2 Extract verb.
    verbs = srl.parse(queryStatement)
    self.logger.debug(f"verbs:{verbs}")
    self.logger.debug(f"SRL-Dump:{srl.results}")

    verb = verbs[0]
    # 2.3 Use both information to identify problem class.
    lemma = wp.getLemma(verb)
    self.logger.debug(f"TargetVerb:{verb}|Lemma:{lemma}")
    detectedClass = msc.getProblemClass(lemma)
    self.logger.debug(f"ProblemClass:{ProblemClass.getName(detectedClass)}")

    # 3. Process each statements according to the problem class.  
    statements = sentences[wh_sentences.index(False)]
    if(detectedClass == ProblemClass.DEDUCTIVE):
      # extract target_actor and target_entity from question
      # [usually] actor is tag with ARG0
      target_actor = srl.getRole(role="ARG0",verb=verb)
      self.logger.debug(f"Actor:{target_actor}")
      # [usually] entity is tag with ARG1 but we have to remove "How many" from the sentences
      target_entity = srl.getRole(role="ARG1",verb=verb)
      self.logger.debug(f"Entity:{target_entity}")

      if(target_entity[0].lower() == 'how'):
        target_entity.pop(0)
        if(target_entity[0].lower() == 'many'):
          target_entity.pop(0)

      # Lemmatize
      for index in range(len(target_entity)):
        target_entity[index] = wp.getLemma(target_entity[index],'n')

      self.logger.debug(f"Entity-clean:{target_entity}")


    elif(detectedClass == ProblemClass.POSESSIVE):
      pass
    else:
      raise ValueError(f"Incorrect problem class:{detectedClass}") 




main = Main()
main.run()
# main.run()
