from systems.LoggerFactory import LoggerFactory
from allennlp.predictors.predictor import Predictor
# import pickle
import yaml
import io

class ProblemClass:
  DIR_KB = "knowledgebase/"
  FILE_DEDUCTIVE = "deductive"

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
    d_name = ProblemClass.DIR_KB + ProblemClass.FILE_DEDUCTIVE
    with io.open(d_name, 'w', encoding='utf8') as outfile:
      yaml.dump(sorted(ProblemClass.DEDUCTIVE_SET), outfile, default_flow_style=False, allow_unicode=True)
    # pickle.dump(ProblemClass.DEDUCTIVE_SET, open( ProblemClass.DIR_KB + ProblemClass.FILE_DEDUCTIVE, 'wb' ) )

  @staticmethod
  def loadKnowledge():
    d_name = ProblemClass.DIR_KB + ProblemClass.FILE_DEDUCTIVE
    with open(d_name, 'r') as stream:
      ProblemClass.DEDUCTIVE_SET = set(yaml.safe_load(stream))
    # ProblemClass.DEDUCTIVE_SET = pickle.load( open( ProblemClass.DIR_KB + ProblemClass.FILE_DEDUCTIVE, 'rb' ) )



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

ProblemClass.loadKnowledge()
print(ProblemClass.DEDUCTIVE_SET)
ProblemClass.DEDUCTIVE_SET.add('consume')
ProblemClass.saveKnowledge()
# msc = MSCorpus.getInstance()
# print(msc.getProblemClass('eat'))