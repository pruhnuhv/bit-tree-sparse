#include <iostream>
#include <vector>
#include <algorithm>
#include <utility>
#include <omp.h>

using namespace std;

// Function to count the number of zeros in a row
pair<int, int> count_zeroes_in_row(const vector<int>& row) {
    int zeroes = 0;
    for (int element : row) {
        if (element == 0)
            zeroes++;
    }
    return make_pair(row.size() - zeroes, zeroes);
}

// Function to compute memory access score between two rows
pair<int, int> mem_access(const vector<int>& row1, const vector<int>& row2, const vector<int>& nzperrow, int cadd) {
    int score12 = 0;
    int score21 = 0;
    for (size_t i = 0; i < row1.size(); ++i) {
        if (!row1[i] && row2[i])
            score12 += 1 * nzperrow[cadd + i];
        if (row1[i] && !row2[i])
            score21 += 1 * nzperrow[cadd + i];
    }
    return make_pair(score12, score21);
}

// Function to compute pairwise memory access patterns
vector<pair<pair<int, int>, int>> pairwise_mem_access(const vector<vector<int>>& matrix) {
    int n = matrix.size();
    vector<pair<pair<int, int>, int>> access_patterns;
    vector<int> nzperrow(matrix[0].size(), 1);

    #pragma omp parallel for
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            pair<int, int> scores = mem_access(matrix[i], matrix[j], nzperrow, 0);
            access_patterns.push_back(make_pair(make_pair(i, j), scores.first));
            access_patterns.push_back(make_pair(make_pair(j, i), scores.second));
        }
    }

    return access_patterns;
}

// Function to compute total memory access score
int total_mem_access(const vector<vector<int>>& matrix, const vector<vector<int>>& actmat, int cadd) {
    vector<int> nzperrow;
    int total_score = 0;
    for (const auto& row : actmat) {
        int rownz = count_zeroes_in_row(row).second;
        nzperrow.push_back(rownz);
    }

    for (size_t idx = 0; idx < matrix[0].size(); ++idx) {
        if (matrix[0][idx]) {
            total_score += 1 * nzperrow[cadd + idx];
        }
    }

    for (size_t i = 0; i < matrix.size() - 1; ++i) {
        int score = mem_access(matrix[i], matrix[i + 1], nzperrow, cadd).first;
        total_score += score;
    }

    cout << "Total Memory Accesses for this config: " << total_score << endl;
    return total_score;
}

int main() {
    vector<vector<int>> matrix = {{0, 1, 0, 1}, {1, 0, 1, 0}, {0, 1, 1, 0}};
    vector<vector<int>> actmat = {{0, 1, 0, 1}, {1, 0, 1, 0}, {0, 1, 1, 0}};
    int cadd = 0;

    vector<pair<pair<int, int>, int>> access_patterns = pairwise_mem_access(matrix);
    int total_score = total_mem_access(matrix, actmat, cadd);
    cout << total_score;
    return 0;
}

