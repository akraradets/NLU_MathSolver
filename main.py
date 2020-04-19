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
from Solver import DeductiveSolver


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
    question = "Sam has 5 apples. Sam eats 3 apples. How many apples did Sam have?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples does Sam have left?"
    # question = "Sam has 5 apples. Sam eats 3 apples. Mark consumes 10 more apples. How many apples does Sam consume?"
    # question = "Sam has 5 apples. Sam eats 3 apples.  Sam eats 10 more apples. How many apples does Sam eat?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples are in Sam's Stomach?"
    # question = "Sam has 5 apples. Sam eats 3 apples. How many apples are with Sam?"
    """ 
    1. Split the string into sentences.
    2. Usually, the last sentence is the query statement. Use that to identify problem class.
      2.a Check the type of question (What, Where, When, Why, How).
      2.a-1 Deciding have
      2.b Extract verb.
      2.c Use both information to identify problem class.
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
    pos_queryStatement = pos_sentences[wh_sentences.index(True)]
    self.logger.debug(f"queryStatement:{queryStatement}")
    # 2.a Check the type of question (What, Where, When, Why, How).
    pass

    # 2.b Extract verb.
    verbs = srl.parse(queryStatement)
    verbs_aux = srl.verbs_aux
    
    self.logger.debug(f"verbs:{verbs}")
    self.logger.debug(f"SRL-Dump:{srl.results}")

    target_verb = srl.getRealVerb(pos_queryStatement)

    if(target_verb in ProblemClass.SET_HAVE):
      """ If the targert verb is 'have', it has to perform 'have' deciding (whether it means 'eat' or 'own') base on the following conditions
      Condition 1: It coexists with an eatable object.
      Condition 2: The sentence is not in the present simple tense. 
      Condition 3: If the sentence is the present simple tense, It must have an adverb of frequency.
      Condition 4: It is the answer to the previous sentence that met the conditions.
      We will implement only the first 2 conditions.
      """
      # Condition 1: It coexists with an eatable object.
      # Extract ARG1
      arg1_phrase = srl.getRole('ARG1',target_verb)
      arg1_phrase_str = ""
      for w in arg1_phrase:
        arg1_phrase_str = f"{arg1_phrase_str}{w} " 
      arg1 = cParser.extractNounPhrase_WhPhrase(arg1_phrase_str)
      mainEntity = wp.getLemma(cParser.extract_noun,'n')
      self.logger.debug(f"Entity:{mainEntity}")
      isEatable = False
      if(mainEntity in ProblemClass.SET_EATABLE):
        isEatable = True
        # Condition 2: The sentence is not in the present simple tense. 
        if((srl.obj_do["isExist"] and srl.obj_do["pos"] in ["VB","VBZ"]) 
        or (srl.obj_do["isExist"] == False and srl.obj_have["isExist"] and srl.obj_have["pos"] in ["VB","VBZ"])):
          # It is present simple tense
          # print(srl.obj_do["isExist"])
          # print(srl.obj_do["pos"] in ["VB","VBZ"])
          # print(srl.obj_do["pos"])
          # print(["VB","VBZ"])
          # print("VBD" in ["VB","VBZ"])
          # print(srl.obj_do["isExist"] == False)
          # print(srl.obj_have["isExist"])
          # print(srl.obj_have["pos"] in ["VB","VBZ"])
          self.logger.debug(f"It is present simple tense")
        else:
          # It is not a present simple tense
          self.logger.debug(f"Override target_verb:'{target_verb}' to 'eat'")
          target_verb = "eat"

      else:
        self.logger.debug(f"Entity:{mainEntity} is not eatable -> EatableSET:{ProblemClass.SET_EATABLE}")

    # 2.c Use both information to identify problem class.
    target_lemma = wp.getLemma(target_verb)
    self.logger.debug(f"TargetVerb:{target_verb}|Lemma:{target_lemma}")
    detectedClass = msc.getProblemClass(target_lemma)
    self.logger.debug(f"ProblemClass:{ProblemClass.getName(detectedClass)}")

    # 3. Process each statements according to the problem class.  
    statements = [sentences[index] for index, isWh in enumerate(wh_sentences) if isWh == False]
    pos_statements = [pos_sentences[index] for index, isWh in enumerate(wh_sentences) if isWh == False]
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

      solver = DeductiveSolver()
      solver.tag(actor=target_actor, entity=target_entity, verb=target_lemma, statements=statements, pos_statements=pos_statements)

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
