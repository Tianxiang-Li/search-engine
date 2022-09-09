import re

def phrase(text_list, stop_words):
    phrases = []
    index = 0
    while index in range(len(text_list) - 2):
        
        if satisfy_phrase(text_list, [index, index + 1, index + 2], stop_words):
            #three terms phrase
            phrase = text_list[index] + " " + text_list[index + 1] + " " + text_list[index + 2]
            phrases.append(re.sub('\.', '', phrase))
            index += 3
        elif satisfy_phrase(text_list, [index, index + 1], stop_words):
            #two terms phrase
            phrase = text_list[index] + " " + text_list[index + 1]
            phrases.append(re.sub('\.', '', phrase))
            index += 2
        else:
            index += 1
    if satisfy_phrase(text_list, [-2, -1], stop_words):
        phrase = text_list[-2] + " " + text_list[-1]
        phrases.append(re.sub('\.', '', phrase))

    return phrases
        
def satisfy_phrase(text_list, indexes, stop_words):
    for i in indexes[:-1]:
        if not text_list[i].isalpha() or (text_list[i] in stop_words):
            return False
    if not re.fullmatch('[a-zA-Z]+\.?', text_list[indexes[-1]]) or (re.search('[a-zA-Z]+', text_list[indexes[-1]]).group(0) in stop_words):
        return False
    return True