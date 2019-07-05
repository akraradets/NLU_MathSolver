from nltk import corpus

class myCorpus:
    def __init__(self):
        print('a')
        corpus.gutenberg.fileids()

    def getData(self):
        print("{0}+{1}j".format(self.real, self.imag))


c = myCorpus()