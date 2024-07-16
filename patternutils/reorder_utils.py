from dissimilarity_utils import * 
def pattern_reorder(matrix, actmat):
    # First, calculate the dissimilarity scores between every pair of rows
    print("Getting Access Patterns to Re-order the rows:")
    access_patterns = pairwise_mem_access(matrix)
    # Create a list of indices representing the order in which to add rows to the reordered matrix
    row_indices = [0]  # Start with the first row
    remaining_indices = set(range(1, len(matrix)))  # Set of remaining row indices

    while remaining_indices:
        # Calculate the dissimilarity scores between the last added row and each remaining row
        last_row_index = row_indices[-1]
        dissimilarity_scores = [(i, access_patterns[(last_row_index, i)]) for i in remaining_indices]
        
        # Sort the remaining row indices by increasing dissimilarity score
        dissimilarity_scores.sort(key=lambda x: x[1])

        # Add the row with the lowest dissimilarity score to the reordered matrix
        next_row_index = dissimilarity_scores[0][0]
        row_indices.append(next_row_index)
        remaining_indices.remove(next_row_index)

    # Reorder the rows in the matrix based on the sorted list of indices
    reordered_matrix = [matrix[i] for i in row_indices]
    print("Row Reordered:")

    return reordered_matrix
