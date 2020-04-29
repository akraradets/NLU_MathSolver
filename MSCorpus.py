from systems.LoggerFactory import LoggerFactory
from allennlp.predictors.predictor import Predictor
import yaml
import io

class ProblemClass:
  DIR_KB = "knowledgebase/"

  DEDUCTIVE = 0
  POSSESSIVE = 1

  FILE_DEDUCTIVE = "deductive.yml"
  FILE_POSSESSIVE = "possessive.yml"
  FILE_EATABLE = "eatable.yml"
  FILE_PERSON_MALE = "person_male.yml"
  FILE_PERSON_FEMALE = "person_female.yml"

  LIST_FILE_CORRUPTED = [False,False]
  LIST_SET = {
      0 : 'DEDUCTIVE',
      1 : 'POSSESSIVE'
    }

  SET_DEDUCTIVE = set({'eat'})
  SET_POSSESSIVE = set({'have', 'be'})

  SET_MEAL = set({'breakfast'})
  SET_EATABLE = set({'apple'})

  SET_DO = set({'do','does','did','done'})
  SET_HAVE = set({'have', 'has', 'had'})

  SET_PERSON_MALE = set()
  SET_PERSON_FEMALE = set()

  @staticmethod
  def getName(enum):
    return ProblemClass.LIST_SET.get(enum, "Invalid numbner")

  @staticmethod
  def updateKnowledge(word1,word2):
    logger = LoggerFactory(ProblemClass).getLogger()
    tempSet = set({word1,word2})
    if(ProblemClass.SET_DEDUCTIVE.isdisjoint(tempSet) == False):
      newWord = tempSet.difference(ProblemClass.SET_DEDUCTIVE)
      ProblemClass.SET_DEDUCTIVE.update(tempSet)
      logger.info(f"SET_DEDUCTIVE update with {newWord}")
    # if(ProblemClass.SET_POSSESSIVE.isdisjoint(tempSet) == False):
    #   newWord = tempSet.difference(ProblemClass.SET_POSSESSIVE)
    #   ProblemClass.SET_POSSESSIVE.update(tempSet)
    #   logger.info(f"SET_POSSESSIVE update with {newWord}")

  @staticmethod
  def saveKnowledge():
    if(ProblemClass.LIST_FILE_CORRUPTED[0] == False):
      deductive = ProblemClass.DIR_KB + ProblemClass.FILE_DEDUCTIVE
      with io.open(deductive, 'w', encoding='utf8') as outfile:
        yaml.dump(sorted(ProblemClass.SET_DEDUCTIVE), outfile, default_flow_style=False, allow_unicode=True)
        
    if(ProblemClass.LIST_FILE_CORRUPTED[1] == False):
      possessive = ProblemClass.DIR_KB + ProblemClass.FILE_POSSESSIVE
      with io.open(possessive, 'w', encoding='utf8') as outfile:
        yaml.dump(sorted(ProblemClass.SET_POSSESSIVE), outfile, default_flow_style=False, allow_unicode=True)

  @staticmethod
  def loadKnowledge(rollback = False):
    logger = LoggerFactory(ProblemClass).getLogger()
    dir_kb = ProblemClass.DIR_KB
    list_set = ProblemClass.LIST_SET
    for enum,name in list_set.items():
      filename = dir_kb + getattr(ProblemClass,f"FILE_{name}")
      fail = True
      try:
        with open(filename, 'r') as stream:
          setattr(ProblemClass,f"SET_{name}",set(yaml.safe_load(stream)))
        fail = False
      except FileNotFoundError as f:
        if(rollback == False): raise f
      except:
        ProblemClass.LIST_FILE_CORRUPTED[getattr(ProblemClass,name)] = True
        if(rollback == False): raise Exception(f"{filename} is corrupted.")
      finally:
        if(fail and rollback):
          logger.error(f"Cannot open file {filename}. Use default set value")

    """ Load Eatable set """
    filename = dir_kb + ProblemClass.FILE_EATABLE
    fail = True
    try:
      with open(filename, 'r') as stream:
        ProblemClass.SET_EATABLE = yaml.safe_load(stream)
      fail = False
    except FileNotFoundError as f:
      if(rollback == False): raise f
    except:
      if(rollback == False): raise Exception(f"{filename} is corrupted.")
    finally:
      if(fail and rollback):
        logger.error(f"Cannot open file {filename}. Use default set value")

    """ Load person_male set """
    filename = dir_kb + ProblemClass.FILE_PERSON_MALE
    fail = True
    try:
      with open(filename, 'r') as stream:
        ProblemClass.SET_PERSON_MALE = yaml.safe_load(stream)
      fail = False
    except FileNotFoundError as f:
      if(rollback == False): raise f
    except:
      if(rollback == False): raise Exception(f"{filename} is corrupted.")
    finally:
      if(fail and rollback):
        logger.error(f"Cannot open file {filename}. Use default set value")

    """ Load person_female set """
    filename = dir_kb + ProblemClass.FILE_PERSON_FEMALE
    fail = True
    try:
      with open(filename, 'r') as stream:
        ProblemClass.SET_PERSON_FEMALE = yaml.safe_load(stream)
      fail = False
    except FileNotFoundError as f:
      if(rollback == False): raise f
    except:
      if(rollback == False): raise Exception(f"{filename} is corrupted.")
    finally:
      if(fail and rollback):
        logger.error(f"Cannot open file {filename}. Use default set value")

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
    if(verb in ProblemClass.SET_DEDUCTIVE):
      return ProblemClass.DEDUCTIVE
    if(verb in ProblemClass.SET_POSSESSIVE):
      return ProblemClass.POSSESSIVE
    raise ValueError(f"verb:{verb} is not belong to any ProblemClass")

# ProblemClass.loadKnowledge(rollback=False)
# print(ProblemClass.DEDUCTIVE_SET)
# ProblemClass.DEDUCTIVE_SET.add('consume')
# ProblemClass.saveKnowledge()
# msc = MSCorpus.getInstance()
# print(msc.getProblemClass('eat'))