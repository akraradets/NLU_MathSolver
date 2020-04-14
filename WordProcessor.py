from systems.LoggerFactory import LoggerFactory
import nltk
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from MSCorpus import ProblemClass

class WordProcessor:
  __instance = None
  
  @staticmethod 
  def getInstance():
    if WordProcessor.__instance == None:
      WordProcessor()
    return WordProcessor.__instance

  def __init__(self):
    if WordProcessor.__instance != None:
      raise Exception("This class is a Singleton!")
    else:
      self.logger = LoggerFactory(self).getLogger()
      self.vn = nltk.corpus.util.LazyCorpusLoader(
          'verbnet3', nltk.corpus.reader.verbnet.VerbnetCorpusReader,
          r'(?!\.).*\.xml')
      self.lemmatizer = WordNetLemmatizer()
      # self.vn.classids('add') # returns ['mix-22.1-2', 'multiply-108', 'say-37.7-1']
      WordProcessor.__instance = self

  def getClass(self,verb):
    lemma = self.getLemma(verb)
    classids = self.vn.classids(lemma) # returns ['mix-22.1-2', 'multiply-108', 'say-37.7-1']
    self.logger.debug(f"verb:{verb}|lemma:{lemma}|class:{classids}")
    return classids

  def getLemma(self,word,pos='v'):
    lemma = self.lemmatizer.lemmatize(word,pos)
    return lemma

  def isSimilar(self,lemma1,lemma2,pos = None):
    max_score, min_score, avg_score = self.calSimilarity(lemma1, lemma2, pos)
    if(max_score == 1):
      ProblemClass.updateKnowledge(lemma1,lemma2)
      return True
    else:
      return False

  def calSimilarity(self,lemma1,lemma2,pos = None):
    max_score = 0
    min_score = 1
    avg_score = 0
    count = 0
    for l1 in wn.lemmas(lemma1,pos):
      for l2 in wn.lemmas(lemma2,pos):
        count = count + 1
        score = l1.synset().path_similarity(l2.synset())
        max_score = max(max_score,score)
        min_score = min(min_score,score)
        avg_score = avg_score + score
    avg_score = avg_score / count
    self.logger.debug(f"Similarity: word:{lemma1} word:{lemma2} pos:{pos} -> max:{max_score} min:{min_score} avg:{avg_score} ")
    return max_score, min_score, avg_score

# wp = WordProcessor.getInstance()
# print(wp.isSimilar('eat','consume','v'))
# wp.getClass('left')
# wp.getClass('are')
# wp.getLemma('are')
