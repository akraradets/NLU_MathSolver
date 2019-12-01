import time
import os.path
from subprocess import Popen, PIPE, STDOUT, check_output


def dependency_parse_penn(tree_file):
    """
    Dependency Parse for a tree file and convert dependency relation string to an object of DependencyObject
    """
    parser_directory = "stanford-parser-full-2018-10-17/stanford-parser.jar"
    now = time.time()
    list_of_dependency_relations = []

    # Execute stanford parser and the mode that accept constituency parse tree as input
    # and product dependency output

    p = Popen("java -cp "+parser_directory+" edu.stanford.nlp.trees.EnglishGrammaticalStructure -outputFormat -treeFile ./constituency_trees/" +
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


dependency_parse_penn("parse_tree2.txt")
