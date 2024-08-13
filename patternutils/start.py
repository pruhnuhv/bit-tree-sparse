import pandas as pd
import numpy as np
from pattern_utils import *
from dissimilarity_utils import *
from reorder_utils import *
from similarity_utils import *
import itertools
import sys
import time
import json
sys.path.append("../common_utils/")
from common_utils import get_R50
print(sys.path)
if __name__ == '__main__':
    weight_matrices, activation_matrices = get_R50()
    input_rows = len(weight_matrices[0][0])
    input_cols = input_rows
    input_matrix = []
    for i in range(input_rows):
        row = []
        for j in range(input_cols):
            row.append(random.random())
        input_matrix.append(row)
    activation_matrices.insert(0, input_matrix)

    layer = 0
    for (wt, act) in zip(weight_matrices, activation_matrices):
        n_rows_wt = len(wt)
        n_cols_wt = len(wt[0])

        n_rows_act = len(act)
        n_cols_act = len(act[0])

        if(n_cols_wt == 9 * n_rows_act):
            print("3x3 Conv")
            new = []
            for i in range(9):
                new.extend(act)
            act = new
            activation_matrices[layer] = new
        
        n_rows_act = len(act)
        n_cols_act = len(act[0])
        
        print(f"Layer {layer-1}: {n_rows_wt} x {n_cols_wt}, {n_rows_act} x {n_cols_act}") 
        layer += 1
        assert n_cols_wt == n_rows_act


    ''' Change Variables Related to On-Chip Storage '''
    k = 250
    NBatch = 1
    maxonchipnz = 16

    #### Runs for all ####

    origacc = []
    pattacc = []
    reoracc = []
    memtraf1 = []
    memtraf2 = []

    total_memory_access1 = 0
    total_memory_access_bef_reorder = 0
    total_memory_access_with_reordering = 0
    print(f"\nTiling Sparse Stationary Matrix (co-ordinate space) with {k} rows per tile.")
    print(f"\nOn Chip Memory Required for this config: " + str(int(k*maxonchipnz/1024)) + "KB")
    layerwise_mem_access_ini = []
    layerwise_mem_access_mid = []
    layerwise_mem_access_fin = []
    layertime = []
    av_diss_before = []
    av_diss_after  = []
    for (idx, matrix) in enumerate(weight_matrices):
        layer_memory_access1 = 0
        try: 
            rows = len(matrix)
            cols = len(matrix[0])
            actrows = len(activation_matrices[idx])
            actcols = len(activation_matrices[idx][0])
            print(f"\n\n\n{idx+1}  Weight dimensions: {rows} x {cols}") 
            print(f"Activation dimensions: {len(activation_matrices[idx])} x {len(activation_matrices[idx][0])}") 
        except:
            print("Incorrect Matrix Dimensions")
        
        '''Tile the matrix according to number of NZs per row'''
        t1 = time.time()
        
        try: 
            layer_memory_access1 = total_mem_access(matrix, activation_matrices[idx], 0)
            nosubpatterns_matrix1 = reduce_subpatterns(matrix)
            matchunks = chunkmat(nosubpatterns_matrix1, k)
        except:
            print("Failed to tile the input matrix")
        
        t2 = time.time() 
        chunk_mem_access_bef_reorder = 0
        chunk_mem_access = 0
        try:
            for cid, matc in enumerate(matchunks):
                t3 = time.time() 
                nosubpatterns_matc = reduce_subpatterns(matc)
                orred_matc = or_op_mtx_k(nosubpatterns_matc, k)
                chunk_mem_access_bef_reorder += total_mem_access(orred_matc, activation_matrices[idx], cid*k)
                reordered_matc = pattern_reorder(orred_matc, activation_matrices[idx])
                matc_mem_access = total_mem_access(reordered_matc, activation_matrices[idx], cid*k) 
                chunk_mem_access += matc_mem_access
                t4 = time.time() 
        except:
            print("Failed to parse and reorder matrix chunks")
        
        t5 = time.time() 
        print(f"Un-optimized Memory Accesses for this layer = {layer_memory_access1}")
        print(f"Bef grouping Memory Accesses for this layer = {chunk_mem_access_bef_reorder}")
        print(f"Aft grouping Memory Accesses for this layer = {chunk_mem_access}")
        
        t6 = time.time() 
        layerwise_mem_access_ini.append(layer_memory_access1)
        layerwise_mem_access_mid.append(chunk_mem_access_bef_reorder)
        layerwise_mem_access_fin.append(chunk_mem_access)
        t7 = time.time() 

        print(f"Average dissimilarity pew new row for matrix: {chunk_mem_access/(actrows*actcols)}")
        # print(f"Reordering Time for this layer: {t5-t1+t7-t6}") 
        layertime.append(t5-t1+t7-t6)
        total_memory_access1 += layer_memory_access1
        total_memory_access_with_reordering += chunk_mem_access
        total_memory_access_bef_reorder += chunk_mem_access_bef_reorder    
        av_diss_before.append(layer_memory_access1/(actrows*actcols))
        av_diss_after.append(chunk_mem_access/(actrows*actcols))

    print(layertime)
    print(f"Un-optimized Memory Accesses Total: {total_memory_access1}")
    print(f"Bef grouping Memory Accesses Total: {total_memory_access_bef_reorder}")
    print(f"Aft grouping Memory Accesses Total: {total_memory_access_with_reordering}")

    print(f"Ini: {layerwise_mem_access_ini}")
    print(f"Mid: {layerwise_mem_access_mid}")
    print(f"Fin: {layerwise_mem_access_fin}")

    print(f"\n\nAverage Dissimilarity Before = {av_diss_before}")
    print(f"\n\nAverage Dissimilarity After  = {av_diss_after}")
    with open('../outputs/dissimilarity.txt', 'w') as file:
        json.dump(layerwise_mem_access_fin, file)
