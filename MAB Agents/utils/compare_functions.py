import numpy as np
import collections

def compare_ngrams(problem1, problem2, data): #comparison function 
    #compares two list of ngrams
    #returns:
        #-1 if ngrams_1 is harder than ngrams_2 (ngrams_1 contains all the ngrams of ngrams_2)
        #1 if ngrams_2 is harder than ngrams_1 (ngrams_2 contains all the ngrams of ngrams_1)
        #0 if neither
    
    ngrams1 = list(data['traces_ngrams'][problem1])
    ngrams2 = list(data['traces_ngrams'][problem2])
    ngrams1_set = set(ngrams1)
    ngrams2_set = set(ngrams2)
    
    l1 = len(ngrams1)
    l2 = len(ngrams2)
    u_l1 = len(ngrams1_set)
    u_l2 = len(ngrams2_set)
    
    if (ngrams1_set == ngrams2_set):
        if (l1 == l2):
            return 0
        elif l1 > l2:
            return -1
        else:
            return 1
    elif l1 == 0:
        return 1
    elif l2 == 0:
        return -1
    elif u_l1 == u_l2:
        return 0
    elif u_l1 > u_l2:
        c = ngrams1_set.intersection(ngrams2_set)
        if c == ngrams2_set:
            return -1
        else:
            return 0
    else:
        c = ngrams1_set.intersection(ngrams2_set)
        if c == ngrams1_set:
            return 1
        else:
            return 0