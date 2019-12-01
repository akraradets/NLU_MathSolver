import nltk
from nltk.grammar import FeatureGrammar

class SyntacticParser:

    def __init__(self):
        self.grammar = FeatureGrammar.fromstring(
            """
            %start S
            S   ->    'a' S 'b'
            S   ->      'a' 'b'
            S   ->      B
            B   ->      'a' 'b'
            """
        )
        self.earley = nltk.parse.EarleyChartParser(self.grammar)

    def earley_chart_parse(self, sentence):
        chart = self.earley.chart_parse(sentence)
        parses = list(chart.parses(self.grammar.start()))
        return parses

parser = SyntacticParser()
parses = parser.earley_chart_parse(['a', 'a', 'b', 'b'])
print(parses)