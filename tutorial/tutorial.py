from nltk import lm 
from nltk.util import bigrams
from nltk.util import everygrams
from nltk.util import flatten
from nltk.lm.preprocessing import pad_both_ends
from nltk.lm.preprocessing import padded_everygram_pipeline
from nltk.lm import MLE

def main():
    # sentences
    # a b c. a b c d e f.
    text = [['a','b','c'],['a','b','c','d','e','f']]
    # text[0] = first sentence
    padded_text = list(pad_both_ends(text[0],n=2))
    # padded_text => ['<s>', 'a', 'b', 'c', '</s>']
    for tup in bigrams(padded_text):
        print(tup)

    # ('<s>', 'a')
    # ('a', 'b')
    # ('b', 'c')
    # ('c', '</s>')
    text = "I have two siblings and three dogs".split()
    padded_text = list(pad_both_ends(text, n=2))
    for tup in everygrams(padded_text,max_len=3):
        print(tup)

    text = ["I have two siblings and three dogs".split(),"I prefer coffee to tea".split()]
    flatten(text)
    # ['I', 'have', 'two', 'siblings', 'and', 'three', 'dogs', 'I', 'prefer', 'coffee', 'to', 'tea']
    train, vocab = padded_everygram_pipeline(3, text)
    lm = MLE(3)
    lm.fit(train,vocab)
    lm.vocab.lookup(['I', 'have', 'one'])
    # ('I', 'have', '<UNK>')
    lm.counts['I']
    # 2
    lm.counts[['I']]['have']
    # 1
    lm.counts[['I','have']]['two']
    # 1
    lm.score('I')
    # 0.1
    lm.logscore('I')
    # -3.321928094887362
    lm.logscore('two')
    # -4.321928094887363
    [word for word in lm.vocab]
    # ['<s>', 'I', 'have', 'two', 'siblings', 'and', 'three','dogs', '</s>', 'prefer', 'coffee', 'to', 'tea', '<UNK>']

    # Best interpolation => KneserNeyInterpolation

    
    import nltk 
    mistake = "hapy"
    words = "apple bag cat dog listing happy living orange".split()
    for w in words:
        print(w ,nltk.edit_distance(mistake, w))

    # apple 4
    # bag 3
    # cat 3
    # dog 4
    # listing 7
    # happy 1
    # living 6
    # orange 5

