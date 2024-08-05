import multiprocessing as mp
from multiprocessing import get_context
from pattern_utils import *

def mem_access(row1, row2, nzperrow, cadd):
    score12 = 0
    score21 = 0
    for i in range(len(row1)):
        if (row1[i] == 0) and row2[i]:
            score12 += 1 * nzperrow[cadd+i] 
        if row1[i] and (row2[i]==0):
            score21 += 1 * nzperrow[cadd+i]
    return (score12, score21)

#def pairwise_mem_access(matrix):
#    access_patterns = {}
#    for i in range(len(matrix)):
#        for j in range(i+1, len(matrix)):
#            scoreij, scoreji = mem_access(matrix[i], matrix[j])
#            access_patterns[(i, j)] = scoreij
#            access_patterns[(j, i)] = scoreji
#
#    return access_patterns

def pairwise_mem_access(matrix):
    n = len(matrix)
    access_patterns = {}
    nzperrow = []
#    for row in actmat:
#        rownz = count_zeroes_in_row(row)[1]
#        nzperrow.append(rownz)
    nzperrow = [1 for i in range(len(matrix[0]))]    
    with get_context("fork").Pool(8) as pool:
    # with mp.Pool() as pool:
        # Map the mem_access function to all (i,j) pairs in parallel
        results = pool.starmap(mem_access, [(matrix[i], matrix[j], nzperrow, 0) for i in range(n) for j in range(i+1, n)])
        
        # Store the results in the access_patterns dictionary
        idx = 0
        for i in range(n):
            for j in range(i+1, n):
                scoreij, scoreji = results[idx]
                access_patterns[(i, j)] = scoreij
                access_patterns[(j, i)] = scoreji
                idx += 1
    
    return access_patterns

def total_mem_access(matrix, actmat, cadd):
    nzperrow = []
    total_score = 0
    for row in actmat:
        rownz = count_zeroes_in_row(row)[1]
        nzperrow.append(rownz)
    
    #total_score = count_zeroes_in_row(matrix[0])[1]*sum(nzperrow)
    for idx, element in enumerate(matrix[0]):
        if element:
            total_score += 1 * nzperrow[cadd+idx]
    for i in range(1, len(matrix)-1):
        score = mem_access(matrix[i], matrix[i+1], nzperrow, cadd)[0]
        total_score += score
    print(f"Total Memory Accesses for this config: {total_score}")
    return total_score
