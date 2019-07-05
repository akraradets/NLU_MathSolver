from logger import Logger

class Main:
    def __init__(self):
        self.className = "Main"
        self.logger = Logger(self.className)
    
    def run(self):
        self.logger.log("debug","Starting...")

main = Main()
main.run()
