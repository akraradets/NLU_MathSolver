from logger import Logger
from nltk import word_tokenize
from nltk import pos_tag

class Main:
    def __init__(self):
        self.className = "Main"
        self.logger = Logger(self.className)
    
    def run(self,example=False):
        self.logger.log("debug","Starting...")
        sents = ['I am batman', 'You are superman']
        if(example is False):
            sents = self.getInput()
        # ['I am batman', 'You are superman']
        sents = self.tokenize(sents)
        # [['I', 'am', 'batman'], ['You', 'are', 'superman']]
        for sent in sents:
            print(pos_tag(sent))
        # print(sents)

    def getInput(self):
        print("Enter Text. When you are done, type Q")
        sentences = []
        while True:
            temp = (input("Enter sentence: "))
            if temp == "Q":
                break
            sentences.append(temp)
        self.logger.log('info',f'Input=>{sentences}')
        return sentences

    def tokenize(self, sentences):
        # ['I am batman', 'You are superman']
        for index in range(len(sentences)):
            sentences[index] = word_tokenize(sentences[index])
        return sentences


main = Main()
main.run(example=True)
# main.run()