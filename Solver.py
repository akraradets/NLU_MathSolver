from systems.LoggerFactory import LoggerFactory
from ConParser import ConParser
from SRL import SRL
from WordProcessor import WordProcessor
from MSCorpus import ProblemClass, MSCorpus

class DeductiveSolver:
  def __init__(self):
    self.logger = LoggerFactory(self).getLogger()
    self.cParser = ConParser.getInstance()
    self.srl = SRL.getInstance()
    self.wp = WordProcessor.getInstance()
    self.msc = MSCorpus.getInstance()


  def tag(self, actor, entity, lemma, statements, pos_statements):
    cParser = self.cParser
    srl = self.srl
    wp = self.wp
    msc = self.msc

    target_actor = actor
    target_entity = entity
    target_lemma = lemma

     # Lemmatize
    for index in range(len(target_entity)):
      target_entity[index] = wp.getLemma(target_entity[index],'n')

    self.logger.debug(f"Entity-clean:{target_entity}")
    
    # Process eact statements
    for index, (statement,pos_statement) in enumerate( zip(statements,pos_statements)  ):
      equation = ""
      self.logger.debug(f"Statement-{index}|statement:{statement}")

      verbs = srl.parse(statement)
      verbs_aux = srl.verbs_aux
      self.logger.debug(f"Statement-{index}|verbs:{verbs}")
      self.logger.debug(f"Statement-{index}|SRL-Dump:{srl.results}")

      verb = srl.getRealVerb(pos_statement)

      if(verb in ProblemClass.SET_HAVE):
        """ If the targert verb is 'have', it has to perform 'have' deciding (whether it means 'eat' or 'own') base on the following conditions
        Condition 1: It coexists with an eatable object.
        Condition 2: The sentence is not in the present simple tense. 
        Condition 3: If the sentence is the present simple tense, It must have an adverb of frequency.
        Condition 4: It is the answer to the previous sentence that met the conditions.
        We will implement only the first 2 conditions.
        """
        # Condition 1: It coexists with an eatable object.
        # Extract ARG1
        mainEntity = srl.getRole('ARG1',verb)
        # arg1PhraseStr = ""
        # for w in arg1Phrase:
        #   arg1PhraseStr = f"{arg1PhraseStr}{w} " 
        # arg1 = cParser.extractNounPhrase_WhPhrase(arg1PhraseStr)
        # mainEntity = wp.getLemma(cParser.extract_noun,'n')
        self.logger.debug(f"Statement-{index}|Entity:{mainEntity}")
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
            self.logger.debug(f"Statement-{index}|It is present simple tense")
          else:
            # It is not a present simple tense
            self.logger.debug(f"Statement-{index}|Override verb:'{verb}' to 'eat'")
            verb = "eat"

        else:
          self.logger.debug(f"Statement-{index}|Entity:{mainEntity} is not eatable -> EatableSET:{ProblemClass.SET_EATABLE}")

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
        entityStr = f"{entityStr}{word} "
      self.logger.debug(f"Statement-{index}|entityStr:{entityStr}")
      # extract number from entity
      entityStr_pos = cParser.parse(entityStr)
      self.logger.debug(f"Statement-{index}|entityStr_pos:{entityStr_pos}")
      number = None
      if('CD' in entityStr_pos):
        number = entity.pop(entityStr_pos.index('CD'))
      # Lemmatize
      for i in range(len(entity)):
        entity[i] = wp.getLemma(entity[i],'n')

      self.logger.debug(f"Statement-{index}|Entity-clean:{target_entity}")
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