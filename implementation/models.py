from query_parsing import *
import math

def models(q_tfs, rtrvl_type, index):
    df = index.df
    d_vector = index.d_vector
    total_terms = index.total_terms 
    collection_tfs = index.collection_tfs 
    doc_lengths = index.doc_lengths
    avgdl = total_terms/ len(d_vector)
    scores = []
    for q_id in sorted(q_tfs.keys()):
        # each query id in query term frequency list
        temp = None
        if rtrvl_type == 'cosine':
            idf = get_cos_idf(df, len(d_vector))
            temp = cosine(q_tfs[q_id], idf, d_vector)
        elif rtrvl_type == 'bm25':
            idf = get_bm25_idf(df, len(d_vector))
            temp = bm25(q_tfs[q_id], idf, d_vector, avgdl, doc_lengths)
        else:
            #retrival type is language model
            temp = lm(q_tfs[q_id], d_vector, total_terms, avgdl, collection_tfs, doc_lengths)

        individual_scores = sorted(temp.items(), key = lambda x: x[1], reverse = True)
        
        if len(individual_scores) > 100:
            individual_scores = individual_scores[0:100]
        scores.append([q_id, individual_scores])
    return scores

############################################################################################################
###                                                cosine                                                ###
############################################################################################################

def cosine(q_tf, idf, d_vector):
    temp = {}
    q_weights, q_cos_deno = term_weight_cos_denominator(q_tf, idf)
    d_weights = {}
    for d_id in d_vector:
        d_weights[d_id], d_cos_deno = term_weight_cos_denominator(d_vector[d_id], idf)
        for w_id in q_tf:
            q_weight = q_weights[w_id]
            if w_id in d_weights[d_id]:
                d_weight = d_weights[d_id][w_id]
                dot_product = q_weight * d_weight
                cosine = dot_product / math.sqrt(q_cos_deno * d_cos_deno)
                if d_id not in temp:
                    temp[d_id] = cosine
                else:
                    temp[d_id] += cosine
            
    #finished calculating the scores
    return temp                
    ################  need sort the scores  ###########################


def term_weight_cos_denominator(tfs, idf):
    #calculate the term weights and the denominator for cosine model
    t_weights = {}
    cos_denominator = 0
    denominator = 0
    for t_id in tfs:
        denominator += ((math.log(tfs[t_id], 10) + 1) * idf[t_id]) ** 2
        cos_denominator += tfs[t_id] ** 2
    for t_id in tfs:
        # term weights are naturalized tf-idf
        t_weights[t_id] = (math.log(tfs[t_id], 10) + 1) * idf[t_id]/denominator
    return t_weights, cos_denominator

def get_cos_idf(df, dlength):
    idf = {}
    for t_id in df:
        idf[t_id] = math.log(dlength / df[t_id], 10)
    return idf

############################################################################################################
###                                                 bm25                                                 ###
############################################################################################################

def bm25(q_tf, idf, d_vector, avgdl, doc_lengths):
    k1 = 1.2
    k2 = 500
    b = 0.75
    temp = {}
    for d_id in d_vector:
        dlength = doc_lengths[d_id]
        for w_id in q_tf:
            qtf = q_tf[w_id]
            if w_id in d_vector[d_id]:
                dtf = d_vector[d_id][w_id]
                w = idf[w_id]
                bm_25 = w * ((k1 + 1) * dtf / (dtf + k1 *(1 - b + b * dlength / avgdl))) * ((k2 + 1) * qtf / (k2 + qtf))
                if d_id not in temp:
                    temp[d_id] = bm_25
                else:
                    temp[d_id] += bm_25
    return temp

def get_bm25_idf(df, dlength):
    idf = {}
    for t_id in df:
        idf[t_id] = math.log((dlength - df[t_id] + 0.5) / (df[t_id]+0.5), 10)
    return idf

############################################################################################################
###                                            language model                                            ###
############################################################################################################

def lm(q_tf, d_vector, total_terms, avgdl, collection_tfs, doc_lengths):
    temp = {}
    mu = avgdl
    for d_id in d_vector:
        is_relevent = False
        dlength = doc_lengths[d_id]
        lm_to_add = 0
        for w_id in q_tf:
            if w_id in d_vector[d_id]:
                is_relevent = True
                dtf = d_vector[d_id][w_id]
            else:
                dtf = 0
            ctf = collection_tfs[w_id]
            
            lm_to_add += math.log((dtf + (mu * ctf / total_terms)) / (dlength + mu), 10)

        if is_relevent:
            temp[d_id] = lm_to_add

    return temp

