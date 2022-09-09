import argparse
import argparse
import os
import re
from models import *
from query_parsing import *
from pre_processing import *
from special_token import *
from phrases import *
from stem import *
from models import *
from build import word_build, single_preprocess, stem_preprocess, phrase_preprocess, positional_preprocess
from statistics import mean
import time
def main():
    # command line argument parser
    t_begin = time.perf_counter()
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument('index_directory', help = "a valid directory is required", type = str)
    cmd_parser.add_argument('query_file_path', help = "a valid query file path is required", type = str)
    cmd_parser.add_argument('result_file', help = "a path where the index and lexicon files will be written", type = str)
    cmd_args = cmd_parser.parse_args()

    rtrvl_type = 'lm' # set the retrival type
    scope = 10 # set the range of positions
    expected_retrieval = 70 # set the expected retrieval from phrase and positional index
    output_path_list = cmd_args.result_file.split('/')[:-1]
    output_path = '/'.join(output_path_list)
    query_filename = cmd_args.query_file_path
    output_filename = os.path.join(cmd_args.result_file + '.txt')
    
    scores = []

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

    query_list = parse_query(query_file, '', True)
    query_ids = list(query_list.keys())
    query_ids.sort()
    query_yet_to_parse = query_list.copy()
    for idx_type in ['phrase', 'positional']:
        idx_filename = os.path.join(cmd_args.index_directory + '/' + idx_type + '.txt')
        try:
            idx_file = open(idx_filename)
        except :
            print("cannot open phrase index file")
            exit(1)
    
        
        index = Index(idx_file, idx_type)
        query_list_phrase = dynamic_query_preprocessing(query_yet_to_parse, idx_type)
        all_tfs = query_tf(query_list_phrase, index.lexicon)
        if idx_type == 'phrase':
            #start with phrase index
            # check the phrase df 
            df_mean = mean(list(index.df.values()))
            valid_qtfs = {}
            for q_id in all_tfs:
                use_current_index = False
                if all_tfs[q_id]:
                    for w_id in all_tfs[q_id]:
                        if index.df[w_id] >= df_mean:
                            use_phrase_index = True
                    if use_phrase_index:
                        valid_qtfs[q_id] = all_tfs[q_id]
            #find the scores using phrase index
            phrase_scores = models(valid_qtfs, rtrvl_type, index)
            # delete those queries from yet to parse list
            for q_score in phrase_scores:
                q_id = q_score[0]
                del query_yet_to_parse[q_id]
        elif idx_type == 'positional':
            relevant_ds = []
            for q_id in all_tfs:
                qwps = {}
                relevant_d = []
                for d_id in index.positions:
                    relevant = True
                    for w_id in all_tfs[q_id]:
                        if (w_id not in index.positions[d_id]) or not relevant:
                            relevant = False
                            break
                        else:
                            current_word_positions = index.positions[d_id][w_id]
                            if qwps != {}:
                                for w_id in qwps:
                                    is_close = False
                                    for p in qwps[w_id]:
                                        for q in current_word_positions:
                                            if abs(p - q) < scope:
                                                is_close = True
                                    if not is_close:
                                        relevant = False
                                        break
                            qwps[w_id] = current_word_positions
                    if relevant:
                        relevant_ds.append(d_id)
            index = index.find_relevant(relevant_ds)
            positional_scores = models(all_tfs, rtrvl_type, index)
    #finished using phrase index and positional index
    scores = phrase_scores + positional_scores
    scores.sort(key = lambda x: x[0])

    #check if retrieved enough document, if not, use stem index
    idx_type = 'stem'
    query_yet_for_stem = {}
    doc_in_score = {}
    for queryid in query_ids:
        num_doc = 0
        doc_in_score[queryid] = []
        for score in scores:
            if queryid == score[0]:
                num_doc = len(score[1])
                for dsc in score[1]:
                    doc_in_score[queryid].append(dsc[0])
        if num_doc <= expected_retrieval:
            query_yet_for_stem[queryid] = query_list[queryid]
    
    query_list_stem = dynamic_query_preprocessing(query_yet_for_stem, idx_type)
    idx_filename = os.path.join(cmd_args.index_directory + '/' + idx_type + '.txt')
    try:
        idx_file = open(idx_filename)
    except :
        print("cannot open phrase index file")
        exit(1)
    index = Index(idx_file, idx_type)
    stem_tfs = query_tf(query_list_stem, index.lexicon)
    stem_scores = models(stem_tfs, rtrvl_type, index)

    for s in stem_scores:
        q_id = s[0]
        q_sc = s[1]
        added = False
        for sc in scores:
            qsc_id = sc[0]
            qsc_sc = sc[1]
            if q_id == qsc_id:
                # append to the query score list
                for d_sc in q_sc:
                    if d_sc[0] not in doc_in_score[qsc_id]:
                        qsc_sc.append(d_sc)
                added = True
        if not added:
            scores.append(s)
    scores.sort(key = lambda x: x[0])


    for query in scores:
        q_id = query[0]
        d_scs = query[1]
        
        for index in range(len(d_scs)):
            d_sc = d_scs[index]
            d_id = d_sc[0]
            comment = rtrvl_type
            if d_id not in doc_in_score[q_id]:
                comment += '-stem'
            elif q_id in valid_qtfs:
                comment += '-phrase'
            else:
                comment += '-positional'
            sc = d_sc[1]
            ro = index + 1
            out_line = str(q_id) + ' ' + '0' + ' ' + d_id + ' ' + str(ro) + ' ' + str(sc) + ' ' + comment + '\n'
            
            output_file.write(out_line)

            
    t_end = time.perf_counter()
    print("time overlap overall: " + str((t_end - t_begin) * 1000) + " milliseconds")

if __name__ == '__main__':
    main()