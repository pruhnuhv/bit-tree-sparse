import scipy.sparse as sparse
import numpy as np
import math
import os
import random
import sys
import argparse
sys.path.append("../common_utils/")
print(sys.path)
from common_utils import get_R50



parser = argparse.ArgumentParser(description='Script with bitwidth input')
parser.add_argument('--bitwidth', type=int, default=4, help='Bit width (default: 4)')
args = parser.parse_args()
bitwidth = args.bitwidth
print(f"Using bitwidth: {bitwidth}")
# bitwidth = 4
idwidth = 16

# Function to calculate storage space required for CSR format
def csr_storage_space(matrix): 
    csr = matrix.nonzero()[0] 
    nnz = len(csr) 
    rowptrs = len(set(csr))
    #storage_space = 4*(nnz*2 + rowptrs)
    storage_space = ((bitwidth * nnz) + (idwidth * (nnz + rowptrs))) / 8 
    return storage_space / 1e6

# Function to calculate storage space required for COO format
def coo_storage_space(matrix):
    coo = matrix.nonzero()[0]
    nnz = len(coo)
    storage_space = ((bitwidth * nnz) + (idwidth * (nnz + nnz))) / 8 
    return storage_space / 1e6

# Function to calculate storage space required for dense format
def dense_storage_space(matrix):
    n_rows = len(matrix)
    n_cols = len(matrix[0])
    storage_space = bitwidth * n_rows * n_cols / 8
    return storage_space / 1e6

# Function to calculate storage space required for dense format
def nm_storage_space(matrix):
    N = 2
    M = 4
    n_rows = len(matrix)
    n_cols = len(matrix[0])
    depth = int(math.ceil(n_rows * n_cols / M))
    storage_space = ((N * depth * bitwidth) + (math.log(M, 2) * depth))/8
    return storage_space / 1e6

# Function to calculate storage space required for Bit-vector format
def bitvec_storage_space(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    bitmask = []
    nnz = 0
    for i in range(rows):
        bitmask_row = []
        for j in range(cols):
            bitmask_row.append(1 if matrix[i][j] != 0 else 0)
        bitmask.append(bitmask_row)
        nnzrow  = bitmask_row.count(1)
        nnz += nnzrow
    storage_space = (rows*cols + bitwidth*nnz)/8
    return storage_space / 1e6

def bitree_storage_space(matrix):
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
    for row in bitmask:
        nnzrow  = row.count(1)
        nnz = nnz + nnzrow
        for i in range(0, len(row)-3, 4):
            curr_vector = row[i:i+4]
            if curr_vector.count(1):
                bitree.append(1)
            else:
                bitree.append(0)
    storage_space = (4*bitree.count(1) + bitree.count(0) + bitwidth*nnz)/8
    #print(bitree)
    return storage_space/1e6

def create_sparse_matrix(sparsity, rows=1000, cols=1000):
    """
    Function to create a sparse matrix with given sparsity.

    Parameters:
        sparsity (float): The desired sparsity of the matrix.
        rows (int): Number of rows in the matrix. Default is 1000.
        cols (int): Number of columns in the matrix. Default is 1000.

    Returns:
        list of lists: A 2D list representing a sparse matrix with the specified sparsity.
    """
    # Calculate the number of non-zero elements
    num_nonzero = int((1 - sparsity) * rows * cols)

    # Create an empty 2D list
    matrix = [[0 for _ in range(cols)] for _ in range(rows)]

    # Set some of the elements to non-zero values
    nonzero_indices = np.random.choice(rows * cols, num_nonzero, replace=False)
    for index in nonzero_indices:
        row_index = index // cols
        col_index = index % cols
        matrix[row_index][col_index] = np.random.randint(1, 10)  # Set non-zero value (random in this case)

    return matrix

ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]

densities = []
#Formats
CSR_space = []
dense_space = []
nm_space = []
COO_space = []
bitvec_space = []
bitree_space = []

# '''Input Data Arrays'''
weight_matrices = []
activation_matrices = []

# '''Data for R50 Layers'''
weight_matrices, activation_matrices = get_R50()
input_rows = len(weight_matrices[0][0])
input_cols = input_rows
input_matrix = []
#for i in range(input_rows):
#    row = []
#    for j in range(input_cols):
#        row.append(random.random())
#    input_matrix.append(row)
#activation_matrices.insert(0, input_matrix)

i = 0
for m, n in zip(weight_matrices, activation_matrices):

    print(f"Dim: {len(m)} x {len(m[0])}, {len(n)} x {len(n[0])}")
    n_rows = len(m)
    n_cols = len(m[0])

    sparse_matrix_csr = sparse.csr_matrix(m)
    sparse_matrix_dense = m
    csr = sparse_matrix_csr.nonzero()[0] 
    nnz = len(csr)
    density = nnz/(len(m)*len(m[0]))
    densities.append(density) 
    
    asparse_matrix_csr = sparse.csr_matrix(n)
    asparse_matrix_dense = n
    acsr = asparse_matrix_csr.nonzero()[0] 
    annz = len(acsr)
    adensity = annz/(len(n)*len(n[0]))
    print(f"Density: {density}, {adensity}")

    ''' Calculate storage space required for CSR format '''
    csr_storage_space_required = csr_storage_space(sparse_matrix_csr)
    csr_storage_space_required += csr_storage_space(asparse_matrix_csr)
    CSR_space.append(csr_storage_space_required)

    ''' Calculate storage space required for N:M format '''
    nm_storage_space_required = nm_storage_space(sparse_matrix_dense)
    nm_storage_space_required += nm_storage_space(asparse_matrix_dense)
    nm_space.append(nm_storage_space_required)

    ''' Calculate storage space required for dense format '''
    dense_storage_space_required = dense_storage_space(sparse_matrix_dense)
    dense_storage_space_required += dense_storage_space(asparse_matrix_dense)
    dense_space.append(dense_storage_space_required)

    ''' Calculate storage space required for CSR format '''
    coo_storage_space_required = coo_storage_space(sparse_matrix_csr)
    coo_storage_space_required += coo_storage_space(asparse_matrix_csr)
    COO_space.append(coo_storage_space_required)

    ''' Calculate storage space required for Bit-Vector format '''
    bitvec_storage_space_required = bitvec_storage_space(sparse_matrix_dense)
    bitvec_storage_space_required += bitvec_storage_space(asparse_matrix_dense)
    bitvec_space.append(bitvec_storage_space_required)

    ''' Calculate storage space required for Bit-Tree format '''
    bitree_storage_space_required = bitree_storage_space(sparse_matrix_dense)
    bitree_storage_space_required += bitree_storage_space(asparse_matrix_dense)
    bitree_space.append(bitree_storage_space_required)

    i = i+1


csr_norm = [x/y for x,y in zip(CSR_space, dense_space)]
coo_norm = [x/y for x,y in zip(COO_space, dense_space)]
bitvec_norm = [x/y for x,y in zip(bitvec_space, dense_space)]
bitree_norm = [x/y for x,y in zip(bitree_space, dense_space)]
print(csr_norm)
print(coo_norm)
print(bitvec_norm)
print(bitree_norm)
print(densities)

import matplotlib.pyplot as plt

# SMALL_SIZE = 16
# MEDIUM_SIZE = 19.5
# BIGGER_SIZE = 23
SMALL_SIZE = 10
MEDIUM_SIZE = 12.5
BIGGER_SIZE = 14

plt.figure(figsize=(12, 4))
plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

plt.ylim(0, 3)
plt.scatter(ids, coo_norm, color='g', label='COO', marker='o')
plt.scatter(ids, csr_norm, color='b', label='CSR', marker='o')
plt.scatter(ids, bitvec_norm, color='y', label='Bit-vector', marker='o')
plt.scatter(ids, bitree_norm, color='r', label='Bit-tree', marker='*')
plt.axhline(y=1, color='r', linestyle='dashed', label="Dense Baseline")
plt.legend()
plt.xlabel("Resnet50 Layers")
plt.ylabel(f"Normalized Storage Costs ({bitwidth}bit)")
plt.title("Storage Overheads")
plt.tight_layout()
plt.savefig(f"../outputs/traffic_{bitwidth}.pdf")
# plt.show()

plt.close()

