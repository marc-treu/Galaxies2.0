import nltk
nltk.download('wordnet')
nltk.download('omw')
from nltk.corpus import wordnet


def synonym_generator(keywords_list):
    keywords_syn = dict()
    for word in keywords_list:
        synset = wordnet.synsets(word,lang='fra')
        synonyms = []
        for syns in synset:
            for l in syns.lemma_names('fra'):
                synonyms.append(l)
        keywords_syn[word] = set(synonyms)

    return keywords_syn



