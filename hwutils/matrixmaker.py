import numpy as np
from scipy.sparse import random
from scipy.sparse import save_npz

M = 512  
K = 4608
N = 49  
S1 = 0.91 
S2 = 0.71 

min_value = 0
max_value = 1000
sparse_matrix = random(M, K, density=1-S1, format='coo', data_rvs=lambda size: np.random.randint(min_value, max_value, size))
sparse_matrix2 = random(K, N, density=1-S2, format='coo', data_rvs=lambda size: np.random.randint(min_value, max_value, size))

dense_matrix = sparse_matrix.toarray()
output_file = "sparse_matrix.txt"
np.savetxt(output_file, dense_matrix, delimiter=' ', fmt = "%d")
print(f"Matrix saved to {output_file}")
dense_matrix = sparse_matrix2.toarray()
output_file = "sparse_matrix2.txt"
np.savetxt(output_file, dense_matrix, delimiter=' ', fmt = "%d")
print(f"Matrix saved to {output_file}")

