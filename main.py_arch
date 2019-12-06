from systems.LoggerFactory import LoggerFactory
# from systems.CorpusFactory import CorpusFactory
from nltk import word_tokenize
from nltk.lm.preprocessing import pad_both_ends
from nltk import pos_tag

class Main:
    def __init__(self):
        self.logger = LoggerFactory(self).getLogger()

    def run(self, nGram=2 , example=False):
        self.logger.debug('Starting...')
        sents = self.getInput(example)
        # ['I am batman', 'You are superman']
        sents = self.tokenize(sents,nGram)
        # [['I', 'am', 'batman'], ['You', 'are', 'superman']]
        self.tagged = self.posTag(sents)
        # print(tagged)
        # return tagged

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

    def tokenize(self, sentences, nGram=2):
        # ['I am batman', 'You are superman']
        for index in range(len(sentences)):
            sent = sentences[index]
            tokenized = word_tokenize(sent)
            padded = list(pad_both_ends(tokenized,n=nGram))
            sentences[index] = padded
            
        self.logger.debug(f'Tokenize=>{sentences}')
        return sentences

    def posTag(self, sentences):
        tagged = []
        for index in range(len(sentences)):
            tagged.append(pos_tag(sentences[index]))
        self.logger.debug(f'Tagged=>{tagged}')
        return tagged

main = Main()
main.run(example=False,nGram=2)
# main.run()
