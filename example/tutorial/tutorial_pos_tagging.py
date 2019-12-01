from nltk.corpus import brown
from nltk import word_tokenize, DefaultTagger, RegexpTagger, FreqDist, ConditionalFreqDist, UnigramTagger, BigramTagger, TrigramTagger
from nltk.tag.util import untag
from nltk.tag import CRFTagger
from sklearn_crfsuite import CRF, metrics
brown_tagged_sents = brown.tagged_sents(categories='news')
brown_sents = brown.sents(categories='news')
brown_global_sent = brown.sents()

def default_tag():
    #Tagging any word by assigning the most frequent tag in a given corpus

    tags = []
    for (word, tag) in brown.tagged_words(categories='news'):
        tags.append(tag)
    most_freq_tag = FreqDist(tags).max()
    raw = 'I love AIT because AIT is interesting and professors here give a lot of challenging assignment'
    tokens = word_tokenize(raw)

    #Here is our tagger, it means in default, it will assign 'NN' tag to a word input
    default_tagger = DefaultTagger('NN') 
    tagged = default_tagger.tag(tokens)
    print(tagged)
    score = default_tagger.evaluate(brown_tagged_sents)
    print(score)

def regex_tag():
    raw = 'I am applying for AIT because I can be with my parents here and I am already granted a scholarship'
    raw_incorrect = 'I love AIT because AIT is interesting and professors here give a lot of challenging assignment'
    patterns = [
    (r'.*ing$', 'VBG'),               # gerunds
    (r'.*ed$', 'VBD'),                # simple past
    (r'.*es$', 'VBZ'),                # 3rd singular present
    (r'.*ould$', 'MD'),               # modals
    (r'.*\'s$', 'NN$'),               # possessive nouns
    (r'.*s$', 'NNS'),                 # plural nouns
    (r'^-?[0-9]+(.[0-9]+)?$', 'CD'),  # cardinal numbers
    (r'.*', 'NN')]                    # nouns (default)
    regexp_tagger = RegexpTagger(patterns)
    tagged = regexp_tagger.tag(word_tokenize(raw))
    tagged_incorrect = regexp_tagger.tag(word_tokenize(raw_incorrect))
    print(tagged)
    print(tagged_incorrect)
    score = regexp_tagger.evaluate(brown_tagged_sents)
    print(score)

def lookup_tag(num_sampling):
    raw = 'I am applying for AIT because I can be with my parents here and I am already granted a scholarship'
    #Get the frequency distribution of the words
    fd = FreqDist(brown.words(categories='news'))
    #Get the most frequent tag of each word in the corpus
    cfd = ConditionalFreqDist(brown.tagged_words(categories='news'))#, backoff=nltk.DefaultTagger('NN'))
    #Get the first 100 most common words
    most_freq_words = fd.most_common(num_sampling)
    #Create a dictionary in form of  a tuple (word, most_likely_tag)
    likely_tags = dict((word, cfd[word].max()) for (word, _) in most_freq_words)
    #Unigram means tag by using its most frequency tag (no context needed) just like unigram in the Ngram topic

    lookup_tagger = UnigramTagger(model=likely_tags)
    tagged = lookup_tagger.tag(word_tokenize(raw))
    print(tagged)
    score = lookup_tagger.evaluate(brown_tagged_sents)
    print(score)

    #What is the problem?
    #Why are there so many None's

def ngram_tagger():
    train_len = int(len(brown_tagged_sents)*0.9)
    print(brown_tagged_sents[train_len:])
    bigram_tagger = BigramTagger(brown_tagged_sents[:train_len])
    score = bigram_tagger.evaluate(brown_tagged_sents[train_len:])
    print(score)
    #Why is it worse than Unigram?!!

def ngram_tag_with_backoff():
    fd = FreqDist(brown.words(categories='news'))
    #Get the most frequent tag of each word in the corpus
    cfd = ConditionalFreqDist(brown.tagged_words(categories='news'))#, backoff=nltk.DefaultTagger('NN'))
    #Get the first 100 most common words
    most_freq_words = fd.most_common(1000000)
    #Create a dictionary in form of  a tuple (word, most_likely_tag)
    likely_tags = dict((word, cfd[word].max()) for (word, _) in most_freq_words)
    #Unigram means tag by using its most frequency tag (no context needed) just like unigram in the Ngram topic
    lookup_tagger = UnigramTagger(model=likely_tags)
    #With Backoff
    train_len = int(len(brown_tagged_sents)*0.9)
    print(brown_tagged_sents[train_len:])
    bigram_tagger = BigramTagger(brown_tagged_sents[:train_len], backoff= lookup_tagger)
    score = bigram_tagger.evaluate(brown_tagged_sents[train_len:])
    print(score)

    #Try trigram with bigram and unigram as backoffs

def transform_to_dataset(tagged_sentences):
    X, y = [], []

    for tagged in tagged_sentences:
        X.append([feature_extract(untag(tagged), index) for index in range(len(tagged))])
        y.append([tag for _, tag in tagged])

    return X, y
    

def crf_tag():
    brown_tagged_sents = brown.tagged_sents(categories='news')
    #print(brown_tagged_sents[0])
    train_len = int(len(brown_tagged_sents)*0.9)
    training_sentences = brown_tagged_sents[:train_len]
    test_sentences = brown_tagged_sents[train_len:]

    X_train, y_train = transform_to_dataset(training_sentences)
    X_test, y_test = transform_to_dataset(test_sentences)

    #print(len(X_train))     
    #print(len(X_test))         
    print(X_train[0])
    print(y_train[0])

    model = CRF()
    model.fit(X_train, y_train)

    raw_sent = ['I', 'am', 'a', 'student']
    sent_feat = [feature_extract(raw_sent, index) for index in range(len(raw_sent))]
    print(list(zip(raw_sent, model.predict([sent_feat])[0])))
    y_pred = model.predict(X_test)
    print(metrics.flat_accuracy_score(y_test, y_pred))



def feature_extract(sentence, index):
    """ sentence: [w1, w2, ...], index: the index of the word """
    return {
        'word': sentence[index],
        'is_first': index == 0,
        'is_last': index == len(sentence) - 1,
        'is_capitalized': sentence[index][0].upper() == sentence[index][0],
        'is_all_caps': sentence[index].upper() == sentence[index],
        'is_all_lower': sentence[index].lower() == sentence[index],
        'prefix-1': sentence[index][0],
        'prefix-2': sentence[index][:2],
        'prefix-3': sentence[index][:3],
        'suffix-1': sentence[index][-1],
        'suffix-2': sentence[index][-2:],
        'suffix-3': sentence[index][-3:],
        'prev_word': '' if index == 0 else sentence[index - 1],
        'next_word': '' if index == len(sentence) - 1 else sentence[index + 1],
        'has_hyphen': '-' in sentence[index],
        'is_numeric': sentence[index].isdigit(),
        'capitals_inside': sentence[index][1:].lower() != sentence[index][1:]
    }


def main():
    #default_tag()
    #regex_tag()
    #lookup_tag(100000)
    #ngram_tagger()
    #ngram_tag_with_backoff()
    crf_tag()
    
if __name__ == "__main__":
    main()
