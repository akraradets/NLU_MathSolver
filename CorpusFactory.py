from nltk import corpus
from logger import Logger

class CorpusFactory:
    def __init__(self):
        self.className = "myCorpus"
        self.logger = Logger(self.className)
        self.corpus = corpus.gutenberg.fileids()


    def getData(self):
        print("{0}+{1}j".format(self.real, self.imag))

c = CorpusFactory()
# Gutenberg
# nltk.corpus.gutenberg.fileids()
# ['austen-emma.txt', 'austen-persuasion.txt', 
# 'austen-sense.txt', 'bible-kjv.txt', 
# 'blake-poems.txt', 'bryant-stories.txt', 
# 'burgess-busterbrown.txt', 'carroll-alice.txt', 
# 'chesterton-ball.txt', 'chesterton-brown.txt',
# 'chesterton-thursday.txt', 'edgeworth-parents.txt', 
# 'melville-moby_dick.txt', 'milton-paradise.txt', 
# 'shakespeare-caesar.txt', 'shakespeare-hamlet.txt', 
# 'shakespeare-macbeth.txt', 'whitman-leaves.txt']
