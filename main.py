from logger import Logger

class Main:
    def __init__(self):
        self.className = "Main"
        self.logger = Logger(self.className)
    
    def run(self):
        self.logger.log("debug","Starting...")
        print(self.getInput())

    def getInput(self):
        print("Enter Text. When you are done, type Q")
        sentences = []
        while True:
            temp = (input("Enter sentence: "))
            if temp == "Q":
                break
            sentences.append(temp)
        return sentences

main = Main()
main.run()
