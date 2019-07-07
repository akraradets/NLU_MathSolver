from LoggerFactory import LoggerFactory
from CorpusFactory import CorpusFactory
from nltk import word_tokenize
from nltk import pos_tag
class Main:
    def __init__(self):
        self.className = "Main"
        self.logger = LoggerFactory(self.className).getLogger()

    def run(self, example=False):
        self.logger.debug('Starting...')
        sents = self.getInput(example)
        # ['I am batman', 'You are superman']
        sents = self.tokenize(sents)
        # [['I', 'am', 'batman'], ['You', 'are', 'superman']]
        tagged = self.posTag(sents)
        print(tagged)

    def getInput(self,example):
        if example == True:
            sentences = ['I am batman', 'You are superman']
            self.logger.info(f'Input-Example=>{sentences}')
            return sentences
        print("Enter Text. When you are done, type Q")
        sentences = []
        while True:
            temp = (input("Enter sentence: "))
            if temp == "Q":
                break
            sentences.append(temp)
        self.logger.info(f'Input=>{sentences}')
        return sentences

    def tokenize(self, sentences):
        # ['I am batman', 'You are superman']
        for index in range(len(sentences)):
            sentences[index] = word_tokenize(sentences[index])
        self.logger.debug(f'Tokenize=>{sentences}')
        return sentences

    def posTag(self, sentences):
        tagged = []
        for index in range(len(sentences)):
            tagged.append(pos_tag(sentences[index]))
        self.logger.debug(f'Tagged=>{tagged}')
        return tagged

main = Main()
main.run(example=True)
# main.run()
