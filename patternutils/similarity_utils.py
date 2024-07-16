def similarity_score(row1, row2): 
    score = 0 
    for i in range(len(row1)): 
        if row1[i] and row2[i]: 
            score += 1 
    return score

def calculate_similarity_scores(matrix):
    similarity_scores = {}
    for i in range(len(matrix)):
        for j in range(i+1, len(matrix)):
            score = similarity_score(matrix[i], matrix[j])
            #if score > 80:
            nz1 = count_zeroes_in_row(matrix[i])[1]
            nz2 = count_zeroes_in_row(matrix[j])[1]
            #print(f"Similarity score of {score} for i,j = {i},{j}. NZ in i = {nz1} and NZ in j = {nz2}")
            similarity_scores[(i, j)] = score
            #similarity_scores[(tuple(matrix[i]), tuple(matrix[j]))] = score
    return similarity_scores


def calculate_total_similarity_score(matrix, similarity_scores): 
    total_score = 0 
    for i in range(len(matrix) - 1): 
        score = similarity_scores.get((i, i+1), similarity_scores.get((i+1, i), 0)) 
        total_score += score 
    return total_score 
 
def reorder_matrix(matrix, similarity_scores): 
    # Sort similarity scores in ascending order 
    sorted_scores = sorted(similarity_scores.items(), key=lambda x: x[1]) 
     
    # Initialize visited rows and re-ordered matrix 
    visited_rows = [] 
    reordered_matrix = [] 
     
    # Choose row with lowest NZ as starting row 
    starting_row = min(enumerate(matrix), key=lambda x: count_zeroes_in_row(x[1])[1])[0] 
    visited_rows.append(starting_row) 
    reordered_matrix.append(matrix[starting_row]) 
     
    # Iterate over sorted similarity scores and add unvisited rows to re-ordered matrix 
    for (i, j), score in sorted_scores: 
        if i in visited_rows and j in visited_rows: 
            continue 
        elif i in visited_rows: 
            if count_zeroes_in_row(matrix[j])[1] < count_zeroes_in_row(reordered_matrix[-1])[1]: 
                visited_rows.append(j) 
                reordered_matrix.append(matrix[j]) 
        elif j in visited_rows: 
            if count_zeroes_in_row(matrix[i])[1] < count_zeroes_in_row(reordered_matrix[-1])[1]: 
                visited_rows.append(i) 
                reordered_matrix.append(matrix[i]) 
     
    # Append any remaining unvisited rows to re-ordered matrix 
    for i in range(len(matrix)): 
        if i not in visited_rows: 
            reordered_matrix.append(matrix[i]) 
     
    return reordered_matrix
