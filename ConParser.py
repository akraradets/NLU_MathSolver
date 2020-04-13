from systems.LoggerFactory import LoggerFactory
from allennlp.predictors.predictor import Predictor

class ConParser:
  __instance = None
  
  @staticmethod 
  def getInstance():
    if ConParser.__instance == None:
        ConParser()
    return ConParser.__instance

  def __init__(self):
    if ConParser.__instance != None:
        raise Exception("This class is a Singleton!")
    else:
        self.logger = LoggerFactory(self).getLogger()
        self.predictor = Predictor.from_path("libs/allennlp-conParser.tar.gz")
        ConParser.__instance = self

  def parse(self, sentence):
    # reset results
    self.results = None
    results = self.predictor.predict(
      sentence=sentence
    )
    # save results
    self.results = results
    # print(results)

cParser = ConParser.getInstance()
print("============== 1 ========================")
cParser.parse("How many apples does Sam eat?")
print("============== 2 ========================")
cParser.parse("How many apples does Sam eat?")