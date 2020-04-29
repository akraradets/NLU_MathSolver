from systems.LoggerFactory import LoggerFactory
import json

class Equation:
  OPER_ADD = 0
  OPER_MINUS = 1
  LIST_OPER = {
    0 : 'ADD',
    1 : 'MINUS'
  }
  LIST_OPER_SYMBOL = {
    0 : '+',
    1 : '-'
  }

  def __init__(self):
    self.logger = LoggerFactory(self).getLogger()
    self.data = []

  @staticmethod
  def getOperName(enum):
    return Equation.LIST_OPER.get(enum, "Invalid numbner")

  @staticmethod
  def getOperSymbol(enum):
    return Equation.LIST_OPER_SYMBOL.get(enum, "Invalid numbner")

  def evalute(self):
    ans = eval(self.prettify())
    return ans
    # for t in enumerate(self.data):

  def add(self,num):
    obj = (Equation.OPER_ADD, num)
    self.data.append(obj)

  def minus(self,num):
    obj = (Equation.OPER_MINUS, num)
    self.data.append(obj)

  def pprint(self):
    s = self.prettify()
    print(s)

  def prettify(self):
    s = ""
    for i,t in enumerate(self.data):
      if i == 0 and t[0] == Equation.OPER_ADD:
        s = t[1]
        continue
      s = f"{s} {Equation.getOperSymbol(t[0])} {t[1]}"
    return s

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    obj = []
    for tup in self.data:
      t = {'operation':Equation.getOperName(tup[0]), 'number':tup[1]}
      obj.append(t)
    return json.dumps(obj)

# e = Equation()
# e.minus(3)
# e.minus(5)
# e.add(10)
# print(e)
# e.pprint()
# print(e.evalute())