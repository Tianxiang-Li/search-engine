from nltk.stem import PorterStemmer

def word_stem(word_list, stop_words):
    stemmer = PorterStemmer()
    stemmed_list = []
    for word in word_list:
        if word not in stop_words:
            word = stemmer.stem(word)
            if word.isalnum():
                stemmed_list.append(word.lower())
    return stemmed_list