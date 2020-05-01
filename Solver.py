from systems.LoggerFactory import LoggerFactory
from Entity import Entity
from Equation import Equation
from MSCorpus import ProblemClass 
from MSCorpus import MSCorpus

class Solver:
  @staticmethod
  def compareEntity(e1,e2,partial=False):
    # check if e1 is ref
    if(e1.type == e1.TYPE_REF_GROUP):
      return True
    c1 = e1.name == e2.name
    c2 = None
    if(partial):
      # if any of them is empty, it is always partial
      if(e1.adjective == set() or e2.adjective == set()):
        c2 = True
      else:
        c2 = not e1.adjective.isdisjoint(e2.adjective)
    else:
      c2 = e1.adjective == e2.adjective
    return c1 and c2

class PossessiveSolver(Solver):
  def __init__(self):
    self.logger = LoggerFactory(self).getLogger()

  def process(self,question):
    msc = MSCorpus.getInstance()
    equation = Equation()
    query = question.getQuerySentence()

    query_actor = Entity(query.getArg(0))
    query_entity = [w for w in query.getArg(1) if ( w.name.lower() not in set({'how','many'}) ) ]
    query_entity = Entity(query_entity)
    query_action = query.getVerb()
    self.logger.debug(f"Query-Extract|action:{query_action.lemma}|actor:{query_actor}|entity:{query_entity}")
    statements = question.getStatementSentences()
    for statement in statements:
      # Extract entity and verb
      state_actor = Entity(statement.getArg(0))
      state_entity = Entity(statement.getArg(1))
      state_action = statement.getVerb()
      self.logger.debug(f"{statement.index}-Extract|action:{state_action.lemma}|actor:{state_actor}|entity:{state_entity}")
      # Check if the sentence is a concerned information or not
      sameActor = Solver.compareEntity(query_actor,state_actor)
      sameEntity = Solver.compareEntity(query_entity,state_entity, partial=True)
      actionClass = msc.getProblemClass(state_action.lemma)
      self.logger.debug(f"{statement.index}-Compare|action:{ProblemClass.getName(actionClass)}|actor:{sameActor}|entity:{sameEntity}")
      if(sameActor and sameEntity):
        if(state_action.lemma == 'have' or actionClass == ProblemClass.POSSESSIVE):
          equation.add(state_entity.quantity)
        elif(actionClass == ProblemClass.DEDUCTIVE):
          equation.minus(state_entity.quantity)
      else:
        print("xxxxxxxx Not a concern sentence. xxxxxxxx")

    return equation