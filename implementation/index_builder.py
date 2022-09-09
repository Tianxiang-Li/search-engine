import re

def single_term_builder(word_list, d_id):
    single_dic = {}
    for word in word_list:
        if word not in single_dic:
            single_dic[word] = [[d_id, 1]]
        else:
            single_dic[word][0][1] += 1
    return single_dic

def positional_builder(word_list, d_id):
    pos_dic = {}
    for index in range(len(word_list)):
        if word_list[index] not in pos_dic:
            pos_dic[word_list[index]] = [[d_id, [index]]]
        else:
            pos_dic[word_list[index]][0][1].append(index)
    return pos_dic

def phrase_builder(phrases, d_id):
    phrase_dic = {}
    for phrase in phrases:
        if phrase not in phrase_dic:
            phrase_dic[phrase] = [[d_id, 1]]
        else:
            phrase_dic[phrase][0][1] += 1
    return phrase_dic
    

def stem_builder(stemmed_list, d_id):
    stem_dic = {}
    for word in stemmed_list:
        if word not in stem_dic:
            stem_dic[word] = [[d_id, 1]]
        else:
            stem_dic[word][0][1] += 1
    return stem_dic

