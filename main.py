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
    self.logger.debug('Load KnowledgeBase')
    ProblemClass.loadKnowledge(rollback=False)
    self.logger.debug('Run question')

    equation = ""
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples does Sam have?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples does Sam have left?"
    question = "Sam has 5 apples. Sam eats 3 apples. Mark consumes 10 more apples. How many apples does Sam consume?"
    # question = "Sam has 5 apples. Sam eats 3 apples.  Sam eats 10 more apples. How many apples does Sam eat?"
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

    target_verb = verbs[0]
    # 2.3 Use both information to identify problem class.
    target_lemma = wp.getLemma(target_verb)
    self.logger.debug(f"TargetVerb:{target_verb}|Lemma:{target_lemma}")
    detectedClass = msc.getProblemClass(target_lemma)
    self.logger.debug(f"ProblemClass:{ProblemClass.getName(detectedClass)}")

    # 3. Process each statements according to the problem class.  
    statements = [sentences[index] for index, isWh in enumerate(wh_sentences) if isWh == False]
    self.logger.debug(f"Statements:{statements}")

    # """ ============== DEDUCTIVE ============== """
    if(detectedClass == ProblemClass.DEDUCTIVE):
      # extract target_actor and target_entity from question
      # [usually] actor is tag with ARG0
      target_actor = srl.getRole(role="ARG0",verb=target_verb)
      self.logger.debug(f"Actor:{target_actor}")
      # [usually] entity is tag with ARG1 but we have to remove "How many" from the sentences
      target_entity = srl.getRole(role="ARG1",verb=target_verb)
      self.logger.debug(f"Entity:{target_entity}")

      if(target_entity[0].lower() == 'how'):
        target_entity.pop(0)
        if(target_entity[0].lower() == 'many'):
          target_entity.pop(0)

      # Lemmatize
      for index in range(len(target_entity)):
        target_entity[index] = wp.getLemma(target_entity[index],'n')

      self.logger.debug(f"Entity-clean:{target_entity}")
      
      # Process eact statements
      for index, statement in enumerate(statements):
        self.logger.debug(f"Statement-{index}|statement:{statement}")
        verbs = srl.parse(statement)
        self.logger.debug(f"Statement-{index}|verb:{verbs}")
        verb = verbs[0]
        lemma = wp.getLemma(verb)
        actor = srl.getRole("ARG0",verb)
        entity = srl.getRole("ARG1",verb)

        # Take 'more' away
        hasMore = False
        if('more' in entity):
          hasMore = True
          entity.pop(entity.index('more'))

        # Construct an entity string for POS
        entityStr = ""
        for word in entity:
          entityStr = f"{entityStr} {word}"
        self.logger.debug(f"Statement-{index}|entityStr:{entityStr}")
        # extract number from entity
        pos = cParser.parse(entityStr)
        self.logger.debug(f"Statement-{index}|entityStr_pos:{pos}")
        number = None
        if('CD' in pos):
          number = entity.pop(pos.index('CD'))
        # Lemmatize
        for i in range(len(entity)):
          entity[i] = wp.getLemma(entity[i],'n')
        
        # Same deduction action
        self.logger.debug(f"Statement-{index}|lemma:{lemma}|actor:{actor}|entity:{entity}|number:{number}")

        # Calculate Similarity of lemma
        if(wp.isSimilar(lemma, target_lemma, 'v') and actor == target_actor and entity == target_entity):
          self.logger.debug(f"Statement-{index}|a concerned phrases")
          if(equation == ""):
            equation = number
          else:
            equation = f"{equation} + {number}"
        else:
          # Probably not relate to our concern
          self.logger.debug(f"Statement-{index}|XXXX not a concerned phrases XXXX")

        print(equation)

    # """ ============== POSSESSIVE ============== """
    elif(detectedClass == ProblemClass.POSSESSIVE):
      
      pass
    else:
      raise ValueError(f"Incorrect problem class:{detectedClass}") 

    ProblemClass.saveKnowledge()
    self.logger.debug(f"Save Knowledgebase")


main = Main()
main.run()
# main.run()
