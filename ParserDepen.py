import time
import os.path
from subprocess import Popen, PIPE, STDOUT, check_output

class ParserDepen:
    def __init__(self):
        self.path = "libs/stanford-parser/"
        self.file = "stanford-parser.jar"
    
    def parse(self, tree_file):
        parser_directory = self.path + self.file
        now = time.time()
        list_of_dependency_relations = []
        p = Popen("java -cp "+parser_directory+" edu.stanford.nlp.trees.EnglishGrammaticalStructure -outputFormat -treeFile ./" +
                  tree_file + " -keepPunct -basic ", shell=True, stdout=PIPE, stderr=STDOUT)
        idx = 0
        # Read the output from stdout
        lines = p.stdout.readlines()
        for val in lines:
            # remove _be from the verb to be
            list_of_dependency_relations.append(val.decode("utf-8").strip('\n'))
            idx = idx + 1

        if(len(list_of_dependency_relations) > 0):
            del(list_of_dependency_relations[idx-1])

        print()
        for relation in list_of_dependency_relations:
            print(relation)

        print("\nDependency Parsing Time Elased (Per one constituency tree): ",
            (time.time() - now), "seconds.\n")

# p = ParserDepen()
# p.parse("tutorial/parse_tree2.txt")
