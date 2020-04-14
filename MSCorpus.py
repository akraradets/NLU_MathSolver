from systems.LoggerFactory import LoggerFactory
from allennlp.predictors.predictor import Predictor
import yaml
import io

class ProblemClass:
  DIR_KB = "knowledgebase/"
  FILE_DEDUCTIVE = "deductive.yml"
  FILE_POSSESSIVE = "possessive.yml"

  DEDUCTIVE = 0
  POSSESSIVE = 1
  DEDUCTIVE_SET = set({'eat'})
  POSSESSIVE_SET = set({'have', 'be'})

  @staticmethod
  def getName(enum):
    definition = {
      ProblemClass.DEDUCTIVE : 'DEDUCTIVE',
      ProblemClass.POSSESSIVE : 'POSSESSIVE'
    }
    return definition.get(enum, "Invalid numbner")

  @staticmethod
  def saveKnowledge():
    deductive = ProblemClass.DIR_KB + ProblemClass.FILE_DEDUCTIVE
    with io.open(deductive, 'w', encoding='utf8') as outfile:
      yaml.dump(sorted(ProblemClass.DEDUCTIVE_SET), outfile, default_flow_style=False, allow_unicode=True)

    possessive = ProblemClass.DIR_KB + ProblemClass.FILE_POSSESSIVE
    with io.open(possessive, 'w', encoding='utf8') as outfile:
      yaml.dump(sorted(ProblemClass.POSSESSIVE_SET), outfile, default_flow_style=False, allow_unicode=True)



  @staticmethod
  def loadKnowledge():
    logger = LoggerFactory(ProblemClass).getLogger()
    try:
      deductive = ProblemClass.DIR_KB + ProblemClass.FILE_DEDUCTIVE
      with open(deductive, 'r') as stream:
        ProblemClass.DEDUCTIVE_SET = set(yaml.safe_load(stream))
    except:
      logger.debug(f"Cannot open file {deductive}. Use default set value")

    try:
      possessive = ProblemClass.DIR_KB + ProblemClass.FILE_POSSESSIVE
      with open(possessive, 'r') as stream:
        ProblemClass.POSSESSIVE_SET = set(yaml.safe_load(stream))
    except:
      logger.debug(f"Cannot open file {possessive}. Use default set value")


class MSCorpus:
  __instance = None
  
  @staticmethod 
  def getInstance():
    if MSCorpus.__instance == None:
      MSCorpus()
    return MSCorpus.__instance

  def __init__(self):
    if MSCorpus.__instance != None:
      raise Exception("This class is a Singleton!")
    else:
      self.logger = LoggerFactory(self).getLogger()
      MSCorpus.__instance = self

  def getProblemClass(self,verb):
    if(verb in ProblemClass.DEDUCTIVE_SET):
      return ProblemClass.DEDUCTIVE
    if(verb in ProblemClass.POSSESSIVE_SET):
      return ProblemClass.POSSESSIVE
    raise ValueError(f"verb:{verb} is not belong to any ProblemClass")

# ProblemClass.loadKnowledge()
# print(ProblemClass.DEDUCTIVE_SET)
# ProblemClass.DEDUCTIVE_SET.add('consume')
# ProblemClass.saveKnowledge()
# msc = MSCorpus.getInstance()
# print(msc.getProblemClass('eat'))