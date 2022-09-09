import argparse
import os
import re
from pre_processing import *
from special_token import *
from index_builder import *
from phrases import *
from stem import *
import statistics
import time
import sys
#from nltk.stem import PorterStemmer

def main():
    t_begin = time.perf_counter()
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument('directory', help = "a valid directory is required", type = str)
    cmd_parser.add_argument('index_type', help = "a valid index type among: single, stem, phrase, positional", type = str)
    cmd_parser.add_argument('output_dir', help = "a directory where the index and lexicon files will be written", type = str)
    cmd_parser.add_argument('-m', dest = 'memory_rest', help = "a valid memory_restriction",type = int, default = 0)
    cmd_args = cmd_parser.parse_args()

    escape_filename = os.path.join(os.getcwd(), 'escape_sequence.txt')
    stop_filename = os.path.join(os.getcwd(), 'stops.txt')
    pre_filename = os.path.join(os.getcwd(), 'prefixes.txt')

    valid_index_type = ['single', 'stem', 'phrase', 'positional']
    
    if not os.path.isdir(cmd_args.output_dir):
        os.mkdir(cmd_args.output_dir)
    output_filename = os.path.join(cmd_args.output_dir, cmd_args.index_type + '.txt')
    
    #memory_restriction
    if cmd_args.memory_rest == 0:
        memory_restriction = sys.maxsize
    else:
        memory_restriction = cmd_args.memory_rest

    # finished memory restriction


    temp_dir = os.path.join(os.getcwd(), 'temp_output')
    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)
    merge_dir = os.path.join(os.getcwd(), 'merge_output')
    if not os.path.isdir(merge_dir):
        os.mkdir(merge_dir)
    temp_id = 0
    if cmd_args.index_type not in valid_index_type:
        print("please enter a valid index type among: single, stem, phrase, positional")
        exit(1)
    try:
        escape_file = open(escape_filename)
    except :
        print("cannot open escape_sequence.txt")
        exit(1)
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
    lexicon = {}
    posting_list = []
    t_id = 0

    for currentfile in os.listdir(cmd_args.directory):
        filename = os.path.join(cmd_args.directory, currentfile)
        
        try:
            cf = open(filename)
        except :
            print("cannot open " + currentfile)
            exit(1)
        

        doc_generator = parse_doc(cf)


        for d_id, d_text in doc_generator:
            # pre-processing
            #remove tag
            removed_tag = remove_tag(d_text)
            #replace escape sequence
            replaced_escape_seq = escape_seq(removed_tag, escape_file)

            if cmd_args.index_type == 'single':
                #single term index
                single_term_text = single_preprocess(replaced_escape_seq, prefix_words, stop_words)
                dic_to_add = single_term_builder(single_term_text, d_id)

            elif cmd_args.index_type == 'phrase':
                #phrase index
                phrases = phrase_preprocess(replaced_escape_seq, stop_words)
                dic_to_add = phrase_builder(phrases, d_id)

            elif cmd_args.index_type == 'positional':
                #positional index
                processed_text = positional_preprocess(replaced_escape_seq)
                #generate positional index
                dic_to_add = positional_builder(processed_text, d_id)
                
            else:
                # stem index
                stemmed_list = stem_preprocess(replaced_escape_seq, prefix_words, stop_words)
                #generate stem index
                dic_to_add = stem_builder(stemmed_list, d_id)

            # build temporary files
            for word in list(dic_to_add):
                if word not in lexicon:
                    lexicon[word] = [t_id, 0]
                    t_id += 1
                posting_list.append([lexicon[word][0], get_id(dic_to_add, word), get_term_frequency(dic_to_add, word)])
                lexicon[word][1] += 1
                if len(posting_list) == memory_restriction: #reach to memory limit
                    posting_list.sort()
                    tempfilename = os.path.join(temp_dir, str(temp_id) + ".txt")
                    tempfile = open(tempfilename, "w")
                    for posting in posting_list:
                        if cmd_args.index_type == 'positional':
                            positions = ','.join([str(elem) for elem in posting[2]])
                            to_write = str(posting[0]) + ' ' + posting[1] +  ' ' + positions
                        else:
                            to_write = ' '.join([str(element) for element in posting])
                        tempfile.write(to_write)
                        tempfile.write('\n')
                    tempfile.close()
                    posting_list = []
                    temp_id += 1
            
        cf.close()
    #write the reset of posting list to txt
    posting_list.sort()
    tempfilename = os.path.join(temp_dir, str(temp_id) + ".txt")
    tempfile = open(tempfilename, "w")
    for posting in posting_list:
        if cmd_args.index_type == 'positional':
            positions = ','.join([str(elem) for elem in posting[2]])
            to_write = str(posting[0]) + ' ' + posting[1] +  ' ' + positions
        else:
            to_write = ' '.join([str(element) for element in posting])
        tempfile.write(to_write)
        tempfile.write('\n')
    tempfile.close()

    t_start_merge = time.perf_counter()
    # write temp files into a total file
    #write a seperate posting list file
    temp_dir_list = os.listdir(temp_dir)
    index = 0
    while index < len(temp_dir_list):
        currentfilepath = os.path.join(temp_dir, str(index) + '.txt')
        mergefilepath = os.path.join(merge_dir, str(index) + '.txt')
        try:
            currentfile = open(currentfilepath, "r")
        except :
            print("cannot open " + currentfile)
            exit(1)
        
        mergefile = open(mergefilepath, "w")

        if index == 0:
            to_write = currentfile.read()
            mergefile.write(to_write)
        else:
            lastmergedpath = os.path.join(merge_dir, str(index-1) + '.txt')
            lastmerged = open(lastmergedpath, "r")
            mgenerator = generating_pl_line(lastmerged)
            cgenerator = generating_pl_line(currentfile)
            m = next(mgenerator, False)
            c = next(cgenerator, False)
            while m or c:
                if not c or (m and pl_less(m, c)):
                    mergefile.write(m)
                    m = next(mgenerator, False)
                else:
                    mergefile.write(c)
                    c = next(cgenerator, False)
            lastmerged.close()

        index += 1
        currentfile.close()
        mergefile.close()

    final_mergefilename = str(index - 1) + '.txt'
    final_mergefile = os.path.join(merge_dir, final_mergefilename)
    final_merge = open(final_mergefile)
    words_of_lexicon = list(lexicon)
    lexicon_to_write = ', '.join(words_of_lexicon)
    try:
        output_file = open(output_filename, "w")
    except :
        print("failed to open output file: " + output_filename)
        exit(1)
    output_file.write(lexicon_to_write)
    output_file.write('\n')
    fmgenerator = generating_pl_line(final_merge)
    for l in fmgenerator:
        output_file.write(l)
    final_merge.close()
    t_finish = time.perf_counter()
    """
    #printing data for analysis
    df = []
    for key in lexicon:
        df.append(lexicon[key][1])
    maxdf = max(df)
    mindf = min(df)
    meandf = statistics.mean(df)
    mediandf = statistics.median(df)
    print("index type: " + cmd_args.index_type)
    print("lexicon size: " + str(t_id))
    print("max df: "+ str(maxdf))
    print("min df: " + str(mindf))
    print("mean df: " + str(meandf))
    print("median df: " + str(mediandf))
    print("memory constraint is: " + str(memory_restriction))
    print("time overlap from begin to merge: " + str((t_start_merge - t_begin) * 1000) + " milliseconds")
    print("time overlap from merge to finish: " + str((t_finish - t_start_merge) * 1000) + " milliseconds")
    print("time overlap overall: " + str((t_finish - t_begin) * 1000) + " milliseconds")
    """
    
    
    #delete the temporary files
    for f in os.listdir(temp_dir):
        currentfilepath = os.path.join(temp_dir, f)
        os.remove(currentfilepath)
    for f in os.listdir(merge_dir):
        currentfilepath = os.path.join(merge_dir, f)
        os.remove(currentfilepath)
    os.rmdir(temp_dir)
    os.rmdir(merge_dir)

        
def pl_less(l1, l2):
    ls1 = l1.split()
    ls2 = l2.split()
    if int(ls1[0]) < int(ls2[0]):
        return True
    elif int(ls1[0]) > int(ls2[0]):
        return False
    else:
        return ls1[1] < ls2[1]

    
    #print(lexicon)
    #print(posting_list)
def generating_pl_line(f):
    for line in f:
        yield line

def parse_doc(f):
    
    # generate lines without comments

    # file_lines is a generator
    file_lines = generate_line(f)
    doc_add = False
    doc_text = ""
    for line in file_lines:
        # find document id
        if line.startswith('<DOCNO>'):
            doc_id = find_id(line)
        
        # flag the text adding
        if line == "<TEXT>\n":
            doc_add = True
        if line == "</TEXT>\n":
            doc_add = False
        # add text
        if doc_add:
            doc_text += line
        
        #reach to the end of the doc
        if line == "</DOC>\n":
            yield_text = doc_text
            doc_text = ""
            yield doc_id, yield_text

def generate_line(f):
    # read line in the file
    for line in f:
        # filter whether the line is a comment or not
        if not line.startswith('<!--') or not line.endswith('-->\n'):
            #yield the line
            yield line

def find_id(line):
    # already identified that the line start with <DOCNO>
    return line.split()[1]

def word_build(f):
    words = []
    for line in f:
        words.append(line.strip())
    return words

def get_id(dic, word):
    return dic[word][0][0]

def get_term_frequency(dic, word):
    return dic[word][0][1]

def single_preprocess(replaced_escape_seq, prefix_words, stop_words):
    # replace special case where there are space in the date expressions
    replaced_date_with_month = date_with_space(replaced_escape_seq)
    #tokenize text into list(all punctuations are kept)
    tokenized_text = tokenize(replaced_date_with_month)

    special_tokens, special_tokenized_text = special_token(tokenized_text, prefix_words)

    processed_text = case_fold(special_tokenized_text)

    single_term_text = processed_text + special_tokens
    #generate single term index
    removed_stop_words = []
    for word in single_term_text:
        if word not in stop_words:
            removed_stop_words.append(word)
    return removed_stop_words

def phrase_preprocess(replaced_escape_seq, stop_words):
    tokenized_text = tokenize_punc(replaced_escape_seq)
    processed_text = case_fold_punc(tokenized_text)
    #generate phrase index
    phrases = phrase(processed_text, stop_words)
    return phrases

def positional_preprocess(replaced_escape_seq):
    #tokenize text into list(all punctuations are kept)
    tokenized_text = tokenize(replaced_escape_seq)
    for index in range(len(tokenized_text)):
        tokenized_text[index] = sub_abbreviations(tokenized_text[index])
        tokenized_text[index] = sub_digit(tokenized_text[index])
    #perform casefolding by turning all the word to lowercase
    processed_text = case_fold(tokenized_text)
    
    return processed_text

def stem_preprocess(replaced_escape_seq, prefix_words, stop_words):
    # replace special case where there are space in the date expressions
    replaced_date_with_month = date_with_space(replaced_escape_seq)
    #tokenize text into list(all punctuations are kept)
    tokenized_text = tokenize(replaced_date_with_month)
    
    special_tokens, special_tokenized_text = special_token(tokenized_text, prefix_words)

    processed_text = case_fold(special_tokenized_text)
    
    stemmed_list = word_stem(processed_text, stop_words)
    return stemmed_list


if __name__ == '__main__':
    main()