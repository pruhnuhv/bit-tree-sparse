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

def pairwise_mem_access(matrix):
    n = len(matrix)
    access_patterns = {}
    nzperrow = []
    nzperrow = [1 for i in range(len(matrix[0]))]    
    try:
        with get_context("fork").Pool(8) as pool:
        # with mp.Pool() as pool:
            results = pool.starmap(mem_access, [(matrix[i], matrix[j], nzperrow, 0) for i in range(n) for j in range(i+1, n)])
            idx = 0
            for i in range(n):
                for j in range(i+1, n):
                    scoreij, scoreji = results[idx]
                    access_patterns[(i, j)] = scoreij
                    access_patterns[(j, i)] = scoreji
                    idx += 1
    except:
        print("Failed to fork memory accessing")
    
    return access_patterns

def total_mem_access(matrix, actmat, cadd):
    nzperrow = []
    total_score = 0
    for row in actmat:
        rownz = count_zeroes_in_row(row)[1]
        nzperrow.append(rownz)
    
    for idx, element in enumerate(matrix[0]):
        if element:
            total_score += 1 * nzperrow[cadd+idx]
    for i in range(1, len(matrix)-1):
        score = mem_access(matrix[i], matrix[i+1], nzperrow, cadd)[0]
        total_score += score
    print(f"Total Memory Accesses for this config: {total_score}")
    return total_score
