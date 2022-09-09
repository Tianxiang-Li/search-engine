import re


def remove_tag(text):
    #remove tag(<...> and </...>)
    return re.sub('[</]+[A-Za-z]+>', ' ', text)


def escape_seq(text, file):
    # replace escape_sequence
    #already removed tag
    for line in file:
        split_line = line.split()
        pattern = split_line[1]
        replacement = split_line[0]
        text = re.sub(split_line[1], split_line[0], text)
    text = re.sub('&[a-zA-Z0-9]+;', ' ', text)
    return text

def tokenize(text):
    #tokenize text into list of words
    #removed tag and replaced escape sequence
    split_text = text.split()
    return split_text

def case_fold(text_list):
    #casefolding on tokenized list of words
    casefolded = []
    for word in text_list:
        word = re.split('[^a-zA-Z0-9\']', word)
        for w in word:
            if w != '':
                if re.fullmatch('[a-zA-Z0-9]+\W+', w) or re.fullmatch('\W+[a-zA-Z0-9]+', w):
                    w= re.sub('\W+', '', w)
                casefolded.append(w.lower())
    return casefolded

def tokenize_punc(text):
    split_text = re.split(' ', text)
    return split_text

def case_fold_punc(text_list):
    #casefolding on tokenized list of words
    casefolded = []
    for word in text_list:
        word = re.split('([^a-zA-Z0-9\'-\.])', word)
        for w in word:
            casefolded.append(w.lower())
    return casefolded