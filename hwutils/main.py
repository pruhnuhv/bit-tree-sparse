from simMatMul import simMatMul
import argparse
import logging
import json
import math
import ast
#from .. import common_utils.get_R50 as get_R50
import sys
sys.path.append("../common_utils/")
print(sys.path)
from common_utils import get_R50
import random

# dis = [1.0, 0.7439139229910714, 1.5392485119047619, 0.6566485969387755, 1.714736627072704, 1.6043233374078798, 0.5629683514030612, 1.5506915656887754, 2.2026494517077664, 0.31728316326530615, 2.5947552116549746, 1.7751539580676021, 0.5563217474489796, 0.7116549744897959, 1.7756574635062359, 0.6324238679846939, 1.652667610012755, 2.1739676339285716, 0.5301937181122449, 4.383594746492347, 2.602995234552154, 0.3818957270408163, 12.406349649234693, 1.7663275271045917, 26.634486607142858, 1.6244569116709184, 2.5835060586734695, 15.429627710459183, 2.2070163026147958, 2.314769788123583, 14.445930325255102, 4.709871253188775, 2.4414926126700682, 14.838887117346939, 4.402851961096939, 2.0001572243480727, 13.59211575255102, 6.836365991709184, 1.8242342509920635, 14.412488042091837, 17.30369100765306, 1.5227543491354876, 27.657047193877553, 8.082270408163266, 3.613768424036281, 14.72413105867347, 14.337163185586734, 1.3361456561791383, 10.492785395408163, 55.53901267538265]


with open('../outputs/dissimilarity.txt', 'r') as file:
    content = file.read()
    dis = ast.literal_eval(content)

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
config = 'hwconfig/cfg1.json'
leaf_size = 4
# '''Simulator Input Data Arrays'''
weight_matrices = []
activation_matrices = []
stall_cycles = []
layer_cycles = []
layer_traffic = []

def bitree(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    bitmask = []
    bitree = []
    nnz = 0
    for i in range(rows):
        bitmask_row = []
        for j in range(cols):
            bitmask_row.append(1 if matrix[i][j] != 0 else 0)
        bitmask.append(bitmask_row)
        nnz += bitmask_row.count(1)
    for row in bitmask:
        bitree_row = []
        for i in range(0, len(row), leaf_size):
            curr_vector = row[i:i+leaf_size]
            if curr_vector.count(1):
                bitree_row.append(1)
            else:
                bitree_row.append(0)
        bitree.append(bitree_row)
    sparsity = nnz/(rows*cols)
    print(f"Matrix Size: {rows}x{cols}, Sparsity: {1-sparsity}")
    return bitmask, bitree, sparsity


def run_layer(layeri, wt, act):
    n_rows_wt = len(wt)
    n_cols_wt = len(wt[0])

    n_rows_act = len(act)
    n_cols_act = len(act[0])
    
    if manual == 0:
        #im2col for 3x3 conv
        if(n_cols_wt == 9 * n_rows_act):
            new = []
            for i in range(9):
                new.extend(act)
            act = new
            activation_matrices[layeri] = new
        
        n_rows_act = len(act)
        n_cols_act = len(act[0])
        
        for row in act:
            pad = 4 - len(row)%4
            for i in range(pad):
                row.append(0)
          
        n_rows_act = len(act)
        n_cols_act = len(act[0])
    
    print(f"\nRunning Layer {layeri+1}: {n_rows_wt} x {n_cols_wt}, {n_rows_act} x {n_cols_act}") 
    assert n_cols_wt == n_rows_act
    bitvec_wt, bitree_wt, s_wt = bitree(wt)
    bitvec_act, bitree_act, s_act = bitree(act)
    
    #setup simulator
    with open(config, 'r') as file:
        data = json.load(file)

    data['dissimilarity'] = int(math.ceil(dis[layeri]))
    accelerator = simMatMul(data)
    accelerator.run(wt, bitvec_wt, act, bitree_act, bitvec_act)
    print(f"Total Cycles, Layer {layeri+1} = {accelerator.run_cycles} \n   Stalls % = {accelerator.stall_cycles/accelerator.run_cycles * 100}")
    print(f"Stall Cycles = {accelerator.stall_cycles}")
    print(f"Absolute Time = {accelerator.run_ms} ms")
    layer_cycles.append(accelerator.run_cycles)
    stall_cycles.append(accelerator.stalls)
    file1 = open(f"../outputs/simulator_outputs/layer_{layeri+1:03}.txt","a")
    file1.write(f"layer:{layeri+1:03}")
    file1.write(f"\nstalls = {accelerator.stall_cycles}")
    file1.write(f"\nfraction = {accelerator.stall_cycles/accelerator.run_cycles}")
    file1.write(f"\ncycles = {accelerator.run_cycles}")
    file1.close()
    accelerator.reset()


manual = 0

if manual == 1:
    # '''Data for manual (single) input test '''
    filename = "sparse_matrix.txt"
    f = open(filename, "r")
    wt = []
    for line in f:
      row = [int(x) for x in line.split()]
      wt.append(row)
    filename = "sparse_matrix2.txt"
    f = open(filename, "r")
    act = []
    for line in f:
      row = [int(x) for x in line.split()]
      act.append(row)
    weight_matrices.append(wt)
    activation_matrices.append(act)
else:
    # '''Data for End-to-End R50 Layers'''
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

print("Booting up the Simulator...")
for layeri, (wt, act) in enumerate(zip(weight_matrices, activation_matrices)):
    run_layer(layeri, wt, act)

print(layer_cycles)
with open('../outputs/ZeD_cycles.txt', 'w') as file:
    json.dump(layer_cycles, file)
