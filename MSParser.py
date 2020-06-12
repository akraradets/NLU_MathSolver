from systems.LoggerFactory import LoggerFactory
from allennlp.predictors.predictor import Predictor
from nltk.tokenize import word_tokenize
# from treelib import Node, Tree
import json

""" Construct a parsetree from ConstituencyParser """
class ParseTree:
  SEARCH_DFS = 0
  SEARCH_BFS = 1

  def __init__(self,root):
    rootNode = ParseNode(root)
    self.root = rootNode
    self.height = 1
    self.appendChildToNode(parent=self.root,children=root['children'])
  
  def appendChildToNode(self,parent,children):
    for node in children:
      pnode = ParseNode(node)
      pnode.setParent(parent)
      parent.addChild(pnode)
      if('children' in node.keys()):
        self.appendChildToNode(parent=pnode,children=node['children'])
      if(pnode.level > self.height): self.height = pnode.level
  
  @staticmethod
  def __callback_print(node):
    str = "|" + "--" * node.level + node.__str__()
    return str + "\n"

  @staticmethod
  def __callback_print_structure(node,noLeaf):
    if(node.isLeaf() == False):
      result = "|" + "--" * node.level + node.nodeType
      return result + "\n"
    return ""

  @staticmethod
  def __callback_compare_word(node,word):
    if(node.word.lower() == word.lower()):
      return node

  def getStructure(self):
    noLeaf = True
    return self.__DFS(callback=ParseTree.__callback_print_structure,cargs=(noLeaf,))

  def search(self,word,search=0):
    if(search == ParseTree.SEARCH_DFS):
      return self.__DFS(callback=ParseTree.__callback_compare_word,cargs=(word,))
    elif(search == ParseTree.SEARCH_BFS):
      return self.__BFS(callback=ParseTree.__callback_compare_word,cargs=(word,))
    else:
      raise ValueError(f"{search} value is invalid.")

  def __DFS(self,callback=None,cargs=()):
    # print(*cargs)
    return self.__recurDFS__(self.root,callback,cargs)

  def __recurDFS__(self,node,callback,cargs):
    result = callback(node,*cargs)
    if(result == True): return node
    for c in node.children:
      childResult = self.__recurDFS__(c,callback,cargs)
      # print(type(childResult))
      if(type(childResult) == type(node)): return childResult
      if(type(childResult) == type('a')): result = result + childResult
    return result

  def __BFS(self,callback,cargs):
    queue = [self.root]
    for node in queue:
      result = callback(node,(*cargs))
      if(type(result) == type(True)): return node
      queue.extend(node.children)

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    return self.__DFS(callback=ParseTree.__callback_print,cargs=())

# from MSParser import ParseTree, ConParser, ParseNode
# sent = "How many apples does Sam eat?"
# cParser = ConParser.getInstance()
# cParser.parse(sent)
# tree = cParser.tree
# p = ParseTree(tree)

class ParseNode:
  def __init__(self,node):
    self.word = node['word']
    self.nodeType = node['nodeType']
    self.attributes = node['attributes']
    self.link = node['link']
    self.children = []
    self.parent = None
    self.level = 0

  def isRoot(self):
    return self.parent == None

  def isLeaf(self):
    return self.children == []

  def addChild(self,node):
    self.children.append(node)
  
  def setParent(self,node):
    self.parent = node
    self.level = node.level + 1

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    obj = {}
    # obj['parent'] = self.parent
    obj['level'] = self.level
    obj['word'] = self.word
    obj['nodeType'] = self.nodeType
    obj['attributes'] = self.attributes
    obj['link'] = self.link
    # obj['children'] = [json.loads(s.__str__()) for s in self.children]
    return json.dumps(obj)




""" ConstituencyParser """
class ConParser:
  __instance = None

  SET_LABEL_QUERY = set({'WRB'})  
  SET_LABEL_VERB = set({'VB','VBD','VBG','VBN','VBP','VBZ'})
  SET_LABEL_NOUN = set({'NN','NNS','NNP','NNPS'})

  @staticmethod 
  def getInstance():
    if ConParser.__instance == None:
      ConParser()
    return ConParser.__instance

  def __init__(self):
    if ConParser.__instance != None:
      raise Exception("This class is a Singleton!")
    else:
      self.logger = LoggerFactory(self).getLogger()
      self.predictor = Predictor.from_path("libs/allennlp-conParser.tar.gz")
      ConParser.__instance = self

  def parse(self, sentence, save=True):
    # reset results
    if(save):
      self.results = None
      self.labels = None
      self.words = None
      self.tree = None
      self.tree_str = None
    
    results = self.predictor.predict(
      sentence=sentence
    )
    # save results
    labels = results['pos_tags']
    if(save):
      self.results = results
      self.labels = labels
      self.words = results['tokens']
      self.tree = results['hierplane_tree']['root']
      self.tree_str = results['trees']
    return labels

  def getPhrase(self, word='have', phraseType='VP'):
    if(word not in self.words):
      raise ValueError(f"Word:{word} is not in '{self.words}'")
    root = self.results['hierplane_tree']['root']
    # if(root['nodeType'] == phraseType and word == word_tokenize(root['word'])[0] ):
    if(root['nodeType'] == phraseType and word in word_tokenize(root['word']) ):
      return root
    child_list = root['children']
    # count = 0
    for node in child_list:
      # print(f"===== {count} =====")
      # print(type(node))
      # print(node)      
      if('children' in node.keys()):
        child_list.extend(node['children'])
      # count = count + 1
      # if(node['nodeType'] == phraseType and word == word_tokenize(node['word'])[0] ):
      if(node['nodeType'] == phraseType and word in word_tokenize(node['word']) ):
        return node

  def extractNounPhrase_WhPhrase(self,phrase):
    self.extract_noun = None
    pos = self.parse(phrase,save=False)
    # words = phrase
    words = word_tokenize(phrase)
    count = 0
    nounPhrase = []
    for w,p in zip(words,pos):
      count = count + 1
      # print(count, w, p)
      # if the first word is not How, we abort mission
      if(count == 1):
        if(w.lower() == "how"):
          continue
        else:
          raise ValueError(f"Phrase:{phrase} is not a 'how' phrases.")

      # check second word
      if(count == 2 and w.lower() == 'many')  :
        continue
        
      nounPhrase.append(w)
      if(p in ConParser.SET_LABEL_NOUN):
        self.extract_noun = w

    self.logger.debug(f"Extract NounPhrase:{nounPhrase} Noun:{self.extract_noun} from WhPhrase:{phrase}")
    return nounPhrase




""" Semantic Role Labeling Parser """
class SRLParser:
  __instance = None
  
  @staticmethod 
  def getInstance():
    if SRLParser.__instance == None:
        SRLParser()
    return SRLParser.__instance

  def __init__(self):
    if SRLParser.__instance != None:
        raise Exception("This class is a Singleton!")
    else:
        self.logger = LoggerFactory(self).getLogger()
        self.predictor = Predictor.from_path("libs/allennlp-SRL.tar.gz")
        SRLParser.__instance = self

  def parse(self, sentence):
    # reset results
    self.results = None
    results = self.predictor.predict(
      sentence=sentence
    )
    # save results
    self.results = results

    words = results['words']
    verbs = []
    auxVerbs = []
    tags = {}
    roles = {}

    for target in results['verbs']:
      tagged_words = []
      roles_set = set()
      isAux = False
      if len(target['tags']) == target['tags'].count('O') + 1:
        isAux = True
      
      # if isAux and withAux == False:
      #   continue

      for word, tag in zip(words, target['tags']):
        suffix = ''
        role = tag
        if tag.find('-') >= 0:
          suffix, role = tag.split('-',1)

        tag = {'word':word,
          'tag':tag,
          'suffix': suffix,
          'role': role}
        tagged_words.append(tag)
        roles_set.add(role)

      if(isAux == False):
        verbs.append(target['verb'])
      auxVerbs.append(target['verb'])
      tags[target['verb']] = tagged_words
      roles[target['verb']] = roles_set

    self.words = words
    self.verbs = verbs
    self.auxVerbs = auxVerbs
    self.tags = tags
    self.roles = roles

    return self.verbs

  def getRoleSet(self, verb):
    role_set = []
    try:
      role_set = self.roles[verb]
    except KeyError:
      raise KeyError(f"{verb} is not found in {self.verbs}. \n The sentence is {self.words}")

    return role_set

  def getRole(self, role, verb, suffix = None):
    # return an array of word that tagged as the query role and verb
    tagged_words = []

    try:
      tagged_words = self.tags[verb]
    except KeyError:
      raise KeyError(f"{verb} is not found in {self.verbs}. \n The sentence is {self.words}")

    # print(tagged_words)

    output = []
    for tagged_word in tagged_words:
      # print(tagged_word)
      if(tagged_word['role'] == role):
        output.append(tagged_word['word'])

    return output
