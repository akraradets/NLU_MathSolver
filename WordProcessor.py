from systems.LoggerFactory import LoggerFactory
import nltk
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer


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


# wp = WordProcessor.getInstance()
# wp.getClass('left')
# wp.getClass('are')
# wp.getLemma('are')