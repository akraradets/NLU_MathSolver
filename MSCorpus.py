from systems.LoggerFactory import LoggerFactory
from allennlp.predictors.predictor import Predictor

class ProblemClass:
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

# msc = MSCorpus.getInstance()
# print(msc.getProblemClass('eat'))