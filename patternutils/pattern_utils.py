import itertools
import random
import math
def is_subpattern(pattern, row):
    has_subpattern = True 
    for i in range(len(row)):
        flag = pattern[i] or not row[i]
        if(not flag):
            has_subpattern = False 
            break
    return has_subpattern

def remove_zero_rows(matrix):
    return [row for row in matrix if any(row)]

def count_zeroes_in_matrix(matrix):
    z = 0
    nz = 0
    zero_rows = 0
    for i, row in enumerate(matrix):
        #count = row.count(0)
        #count_nz = len(row) - count
        #sparsity = count/len(row)*100
        #print("Sparsity in row = " + str(sparsity) + "%")
        count, count_nz = count_zeroes_in_row(row)
        z = z + count
        nz = nz + count_nz
        if (not nz): zero_rows = zero_rows + 1
    return z, nz, zero_rows

def count_zeroes_in_row(row):
    if any(row):
        count = row.count(0)
        count_nz = len(row) - count
        return count, count_nz
    else:
        return len(row), 0


def reduce_subpatterns(matrix):
#    print("Original Size Of Matrix: " + str(len(matrix)))
    matrix = remove_zero_rows(matrix)
#    print("Size of Matrix Without Zero Rows: " + str(len(matrix)))
    i = 0
    ptr = 0
    while i < len(matrix):
        j = i + 1
        while j < len(matrix):
            if is_subpattern(matrix[j], matrix[i]):
                matrix.pop(i)
                i -= 1
                break
            elif is_subpattern(matrix[i], matrix[j]):
                matrix.pop(j)
                j -= 1
            j += 1
        i += 1
#    print("Size of Matrix after removing rows that are just sub patterns: " + str(len(matrix)))
    return matrix

def kth_nonzero_index(lst, k):
    non_zero_list = [i for i, val in enumerate(lst) if val != 0]
    if len(non_zero_list) < k:
        return None  # k is larger than the number of non-zero values in lst
    return non_zero_list[k-1]

def row_splitter (matrix, k):
    new_matrix = []
    for row in matrix:
        nos_splits = count_zeroes_in_row(row)[1] // k
        if (nos_splits == 0):
            new_matrix.append(row)
            #print("\n\nNumber of NZs in the UNCHANGED row being appended: " + str(count_zeroes_in_row(row)[1]))
            continue

        #print("\n\nHit Overhead!: " + str(nos_splits))
        prev_index = 0

        for n in range(1, nos_splits+2):
            new_row = [0]*len(row)

            if n==nos_splits+1:
                index = len(row)
            else:
                index = kth_nonzero_index(row, k*n)

            new_row[prev_index:index] = row[prev_index:index]
            prev_index = index
            #print("Number of NZs in the row being appended: " + str(count_zeroes_in_row(new_row)[1]))
            new_matrix.append(new_row)
            #print(new_row)

    return new_matrix


def generate_patterns(n, l, k):
    patterns = []
    while len(patterns) < n:
        pattern = [0] * l
        ones_indices = random.sample(range(l), k)
        for i in ones_indices:
            pattern[i] = 1
        if pattern not in patterns:
            patterns.append(pattern)
    return patterns

def count_subpatterns(matrix, patterns):
    matrix = remove_zero_rows(matrix)
    for row in matrix:
        for pattern in patterns:
            has_subpattern = is_subpattern(pattern, row)    
            if has_subpattern: break
        
        if has_subpattern:
            z, nz = count_zeroes_in_row(pattern)
        else:
            z, nz = count_zeroes_in_row(row)
            patterns.append(row)
    
    return patterns

def or_op_mtx_k(matrix, k_tile):
    new_matrix = []
    counter = 0
    combined_rows = set()  # to keep track of already combined rows
    rowsize = len(matrix[0])
    numrows = len(matrix)
    k = k_tile*0.80  #utilization
    for i in range(numrows):
        nz_rowi = count_zeroes_in_row(matrix[i])[1]
        if (nz_rowi > k) or (i in combined_rows):
            continue
        or_result = []
        or_result = matrix[i]
        or_success = False
        prev_or_result = []
        nz_oresult = 0
        for j in range(i+1, numrows):

            if nz_oresult > (0.95*k):
                break

            nz_rowj = count_zeroes_in_row(matrix[j])[1]
            if (nz_rowj > k) or (j in combined_rows):
                continue

            or_result = [or_result[l] or matrix[j][l] for l in range(rowsize)]


            nz_oresult = count_zeroes_in_row(or_result)[1]
            if nz_oresult > (k):
                or_result = prev_or_result
                continue

            combined_rows.add(j)
            combined_rows.add(i)
            or_success = True
            prev_or_result = or_result

        if or_success:
            new_matrix.append(or_result)

    # add any remaining uncombined rows to the new matrix
    for i in range(len(matrix)):
        if i not in combined_rows:
            counter = counter + 1
            new_matrix.append(matrix[i])
   
    print("Number of rows combined in Or Operation: " + str(len(combined_rows)))
    print("Uncombined Rows: " + str(counter))
    print("Number of rows after Or Operation: " + str(len(new_matrix)))
    return new_matrix

def chunkmat(matrix, chunk_size):
    # Initialize an empty list to store the chunks
    nchunks = int(math.ceil(len(matrix[0])/chunk_size))
    chunks = [[] for i in range(nchunks)]
    # Loop through the original matrix to create chunks
    for row in matrix:
        cid = 0
        for i in range(0, len(row), chunk_size):
            chunk = row[i:i + chunk_size]  # Extract a chunk of 16 columns
            chunks[cid].append(chunk)
            cid+=1
    return chunks

