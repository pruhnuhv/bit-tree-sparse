from common_utils import get_R50
import random


def matrix_multiply(matrix1, matrix2):
    op = 0
    # Check if matrices are compatible for multiplication
    if len(matrix1[0]) != len(matrix2):
        raise ValueError("Matrices are not compatible for multiplication")

    # Initialize result matrix with zeros
    result_matrix = [[0 for _ in range(len(matrix2[0]))] for _ in range(len(matrix1))]

    # Perform matrix multiplication
    for i in range(len(matrix1)):
        for j in range(len(matrix2[0])):
            for k in range(len(matrix2)):
                result_matrix[i][j] += matrix1[i][k] * matrix2[k][j]
                if matrix1[i][k] * matrix2[k][j] != 0:
                    op += 1
    
    return result_matrix, op/10**6


def sparsity(matrix):
    total_elements = len(matrix) * len(matrix[0])
    non_zero_count = sum(matrix[i][j] != 0 for i in range(len(matrix)) for j in range(len(matrix[0])))
    return (1 - (non_zero_count / total_elements))*100



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
final_sparsities = []
mop_list = []
traffic_list = []
for wt, act in zip(weight_matrices, activation_matrices):
    n_rows_wt = len(wt)
    n_cols_wt = len(wt[0])

    n_rows_act = len(act)
    n_cols_act = len(act[0])

    if(n_cols_wt == 9 * n_rows_act):
    #    print("3x3 Conv")
        new = []
        for i in range(9):
            new.extend(act)
        act = new
        activation_matrices[layer] = new
    
    n_rows_act = len(act)
    n_cols_act = len(act[0])
    
    layer += 1
    print(f"\nRunning Layer {layer}: {n_rows_wt} x {n_cols_wt}, {n_rows_act} x {n_cols_act}") 
    
    for row in act:
        pad = 4 - len(row)%4
        for i in range(pad):
            row.append(0)

    result_matrix, mop = matrix_multiply(wt, act)
    # Calculate sparsity of the resulting matrix
    result_sparsity = sparsity(result_matrix)
    final_sparsities.append(result_sparsity) 
    mop_list.append(mop)
    print(f"Sparsity of the Result Matrix: {result_sparsity}%")

print("\n\n\n\n")
print(final_sparsities)
print(f"MOPs = {mop_list}")
print(f"Average Sparsity of Output Matrix: {sum(final_sparsities)/len(final_sparsities)}")

