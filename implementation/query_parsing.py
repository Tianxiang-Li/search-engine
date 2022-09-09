import re
import os
import math
from nltk.stem import PorterStemmer
from pre_processing import *
from special_token import *
from phrases import *
from stem import *
from build import word_build, single_preprocess, stem_preprocess, positional_preprocess, phrase_preprocess

############################################################################################################
###                                          query processing                                            ###
############################################################################################################

def parse_query(f, index_type, is_dynamic):
    #parse query returns a dictionary of query
    query_list = {}
    query_toadd = False
    query_num = 0
    query_title = ""
    file_lines = generate_line(f)
    doc_add = False
    for file_line in file_lines:
        if file_line == "<top>\n":
            doc_add = True
        if file_line == "</top>\n":
            doc_add = False
        if doc_add and file_line.startswith('<num>'):
            query_num = find_num(file_line)
        if doc_add and file_line.startswith('<title>'):
            query_title = find_title(file_line)
            if not is_dynamic:
                query_list[int(query_num)] = title_parse(query_title, index_type)
            else:
                query_list[int(query_num)] = query_title
    return query_list


def generate_line(f):
    for line in f:
        yield line

def find_num(l):
    return l.split()[-1]



def find_title(l):
    l = re.sub('<title> Topic: ', '', l)
    l = re.sub('[^\S ]', '', l)
    return l

def title_parse(title, idx_type):
    stop_filename = os.path.join(os.getcwd(), 'stops.txt')
    pre_filename = os.path.join(os.getcwd(), 'prefixes.txt')
    try:
        stop_file = open(stop_filename)
        stop_words = word_build(stop_file)
    except :
        print("cannot open stops.txt")
        exit(1)

    try:
        prefix_file = open(pre_filename)
        prefix_words = word_build(prefix_file)
    except :
        print("cannot open prefixes.txt")
        exit(1)
    title_list = []
    if idx_type == 'single':
        title_list = single_preprocess(title, prefix_words, stop_words)
    elif idx_type == 'stem':
        title_list = stem_preprocess(title, prefix_words, stop_words)
    elif idx_type == 'positional':
        title_list = positional_preprocess(title)
    else:
        # phrase index
        title_list = phrase_preprocess(title, stop_words)
    return title_list

def query_tf(query_list, lexicon):
    q_tf = {}
    for q_id in query_list:
        q_tf[q_id] = {}
        for word in query_list[q_id]:
            if word in lexicon:
                w_id = lexicon.index(word)
                if w_id not in q_tf[q_id]:
                    q_tf[q_id][w_id] = 1
                else:
                    q_tf[q_id][w_id] += 1
    return q_tf

#####################################   dynamic query processing    ########################################
def dynamic_query_preprocessing(q_list, idx_type):
    query_list = {}
    for q_id in q_list:
        query_list[q_id] = title_parse(q_list[q_id], idx_type)
    return query_list

############################################################################################################
###                                          index processing                                            ###
############################################################################################################
class Index:
    
    def __init__(self, f, idx_type):
        self.type = idx_type
        self.lexicon = []
        self.df = {}
        self.d_vector = {}
        self.total_terms = 0
        self.collection_tfs = {}
        self.doc_lengths = {}
        self.positions = {}
        lines = idx_lines(f)
        is_lex = True
        for l in lines: 
        #first line is lexicon
            if is_lex:
                self.lexicon = l.split(', ')
                self.lexicon[-1] = self.lexicon[-1].strip()
                is_lex = False
            else:
                #rest are posting list
                p = l.split()
                t_id = int(p[0]) #term id
                d_id = p[1] #document id
                position = []
                if idx_type != 'positional':
                    tf = int(p[2]) #term frequency or position
                else:
                    position_list = p[2].strip().split(',')
                    for i in range(len(position_list)):
                        position.append(int(position_list[i]))
                    tf = len(position)
                self.total_terms += tf
                # accumulate document frequency for each term
                if t_id not in self.df:
                    self.df[t_id] = 1
                else:
                    self.df[t_id] += 1
                
                if t_id not in self.collection_tfs:
                    self.collection_tfs[t_id] = tf
                else:
                    self.collection_tfs[t_id] += tf

                # create document dictionary that has term id corresponding to their term frequency or position
                if d_id not in self.doc_lengths:
                    self.doc_lengths[d_id] = tf
                else:
                    self.doc_lengths[d_id] += tf
                
                if d_id not in self.d_vector:
                    self.d_vector[d_id] = {t_id: tf}
                else:
                    self.d_vector[d_id][t_id] = tf
                
                if idx_type == 'positional':
                    if d_id not in self.positions:
                        self.positions[d_id] = {t_id: position}
                    else:
                        self.positions[d_id][t_id] = position
    def find_relevant(self, relevant_ds):
        vector_temp = {}
        length_temp = {}
        for d_id in self.d_vector:
            if d_id in relevant_ds:
                vector_temp[d_id] = self.d_vector[d_id]
                length_temp[d_id] = self.doc_lengths[d_id]
        self.d_vector = vector_temp
        self.doc_lengths = length_temp
        return self

def idx_lines(f):
    for line in f:
        yield line