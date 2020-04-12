from systems.LoggerFactory import LoggerFactory
from allennlp.predictors.predictor import Predictor

class SRL:
  __instance = None
  

  @staticmethod 
  def getInstance():
    if SRL.__instance == None:
        SRL()
    return SRL.__instance

  def __init__(self):
    if SRL.__instance != None:
        raise Exception("This class is a Singleton!")
    else:
        self.logger = LoggerFactory(self).getLogger()
        self.predictor = Predictor.from_path("libs/allennlp-SRL.tar.gz")
        SRL.__instance = self

  def tag(self, sentence):
    results = self.predictor.predict(
      sentence=sentence
    )

    for verb in results['verbs']:
      if len(verb['tags']) == verb['tags'].count('O') + 1 :
          continue
      print(f"======{verb['verb']}=======")
      for word, tag in zip(results["words"], verb["tags"]):
          print(f"{word}\t{tag}")

# srl = SRL.getInstance()
# srl.tag("Sam eats 3 apples.")

# srl2 = SRL.getInstance()
# srl2.tag("Sam eats 3 apples.")