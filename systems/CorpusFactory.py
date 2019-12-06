from systems.LoggerFactory import LoggerFactory
from nltk import corpus
from nltk import FreqDist, ConditionalFreqDist, UnigramTagger ,BigramTagger

class CorpusFactory:
    def __init__(self):
        self.logger = LoggerFactory(self).getLogger()
        self.corpus = corpus.brown
        cat = 'science_fiction'
        self.logger.info(f'Load Corpus - Brown - {cat}')
        words = self.corpus.words(categories=cat)
        tagged_words = self.corpus.tagged_words(categories=cat)
        tagged_sents = self.corpus.tagged_sents(categories=cat)
        fd = FreqDist(words)
        cfd = ConditionalFreqDist(tagged_words)
        most_freq_words = fd.most_common(1000000)
        likely_tags = dict((word, cfd[word].max()) for (word, _) in most_freq_words)
        self.unigram = UnigramTagger(model=likely_tags)
        train_len = int(len(tagged_sents)*0.9)
        self.bigram = BigramTagger(tagged_sents[:train_len], backoff=self.unigram)

c = CorpusFactory()
# most_freq_words = fd.most_common(1000000)
# #Create a dictionary in form of  a tuple (word, most_likely_tag)
# likely_tags = dict((word, cfd[word].max())
#                     for (word, _) in most_freq_words)
# #Unigram means tag by using its most frequency tag (no context needed) just like unigram in the Ngram topic
# lookup_tagger = UnigramTagger(model=likely_tags)
# #With Backoff
# train_len = int(len(brown_tagged_sents)*0.9)
# print(brown_tagged_sents[train_len:])
# bigram_tagger = BigramTagger(
#     brown_tagged_sents[:train_len], backoff=lookup_tagger)
# score = bigram_tagger.evaluate(brown_tagged_sents[train_len:])
# print(score)


# Gutenberg
# nltk.corpus.gutenberg.fileids()
# ['austen-emma.txt', 'austen-persuasion.txt', 
# 'austen-sense.txt', 'bible-kjv.txt', 
# 'blake-poems.txt', 'bryant-stories.txt', 
# 'burgess-busterbrown.txt', 'carroll-alice.txt', 
# 'chesterton-ball.txt', 'chesterton-brown.txt',
# 'chesterton-thursday.txt', 'edgeworth-parents.txt', 
# 'melville-moby_dick.txt', 'milton-paradise.txt', 
# 'shakespeare-caesar.txt', 'shakespeare-hamlet.txt', 
# 'shakespeare-macbeth.txt', 'whitman-leaves.txt']
