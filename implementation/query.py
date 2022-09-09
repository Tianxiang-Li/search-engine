import argparse
import argparse
import os
import re
from query_parsing import *
from pre_processing import *
from special_token import *
from phrases import *
from stem import *
from models import *
from build import word_build, single_preprocess, stem_preprocess
import time
def main():
    # command line argument parser
    t_begin = time.perf_counter()
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument('index_directory', help = "a valid directory is required", type = str)
    cmd_parser.add_argument('query_file_path', help = "a valid query file path is required", type = str)
    
    cmd_parser.add_argument('retrieval_model', help = "a valid retrieval model: cosine, bm25, lm", type = str)
    cmd_parser.add_argument('index_type', help = "a valid index type among: single, stem", type = str)
    cmd_parser.add_argument('result_file', help = "a path to the results file", type = str)
    
    cmd_args = cmd_parser.parse_args()

    output_path_list = cmd_args.result_file.split('/')[:-1]
    output_path = '/'.join(output_path_list)
    query_filename = cmd_args.query_file_path
    output_filename = os.path.join(cmd_args.result_file + '.txt')
    #cmd arguments check validity
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    try:
        query_file = open(query_filename)
    except :
        print("cannot open query file")
        exit(1)
    try:
        output_file = open(output_filename, "w")
    except :
        print("failed to open output file: " + output_filename)
        exit(1)
    
    if cmd_args.index_type != 'single' and cmd_args.index_type != 'stem':
        print("please enter a valid index type among: single, stem")
        exit(1)
    valid_model = ['cosine', 'bm25', 'lm']
    if cmd_args.retrieval_model not in valid_model:
        print("please enter a valid retrieval model among: cosine, bm25, lm")
        exit(1)

    #store index type and retrieval model
    idx_type = cmd_args.index_type
    rtrvl_type = cmd_args.retrieval_model
    
    #process index
    index_filename = os.path.join(cmd_args.index_directory, idx_type + '.txt')
    try:
        index_file = open(index_filename)
    except :
        print("failed to open index file " + idx_type + '.txt, check if the file is correct.')
        exit(1)
    index = Index(index_file, idx_type) # retrieve the lexicon, document frequency, document vector, total number of documents
    #"""
    query_list = parse_query(query_file, idx_type, False)
    q_tfs = query_tf(query_list, index.lexicon)
    
    scores = models(q_tfs, rtrvl_type, index)

    for query in scores:
        q_id = query[0]
        d_scs = query[1]
        for index in range(len(d_scs)):
            d_sc = d_scs[index]
            d_id = d_sc[0]
            sc = d_sc[1]
            ro = index + 1
            out_line = str(q_id) + ' ' + '0' + ' ' + d_id + ' ' + str(ro) + ' ' + str(sc) + ' ' + rtrvl_type + '\n'
            output_file.write(out_line)
    #"""
    t_end = time.perf_counter()
    print("time overlap overall: " + str((t_end - t_begin) * 1000) + " milliseconds")

if __name__ == '__main__':
    main()