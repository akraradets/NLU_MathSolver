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
    self.labels = None
    self.words = None
    
    results = self.predictor.predict(
      sentence=sentence
    )
    # save results
    self.results = results
    self.labels = results['pos_tags']
    self.words = results['tokens']
    return self.labels

# cParser = ConParser.getInstance()
# pos = cParser.parse("How many apples does Sam eat?")
# words = cParser.words
# for w,p in zip(words,pos):
#   print(w,p)