#include <iostream>
#include <vector>
#include <algorithm>
#include <tuple>

using namespace std;

bool is_subpattern(const vector<int>& pattern, const vector<int>& row) {
    bool has_subpattern = true;
    for (size_t i = 0; i < row.size(); ++i) {
        bool flag = pattern[i] || !row[i];
        if (!flag) {
            has_subpattern = false;
            break;
        }
    }
    return has_subpattern;
}

vector<vector<int>> remove_zero_rows(const vector<vector<int>>& matrix) {
    vector<vector<int>> result;
    for (const auto& row : matrix) {
        if (any_of(row.begin(), row.end(), [](int x) { return x != 0; })) {
            result.push_back(row);
        }
    }
    return result;
}

pair<int, int> count_zeroes_in_matrix(const vector<vector<int>>& matrix) {
    int z = 0;
    int nz = 0;
    int zero_rows = 0;
    for (const auto& row : matrix) {
        int count, count_nz;
        tie(count, count_nz) = count_zeroes_in_row(row);
        z += count;
        nz += count_nz;
        if (count_nz == 0) {
            zero_rows++;
        }
    }
    return make_pair(z, nz);
}

pair<int, int> count_zeroes_in_row(const vector<int>& row) {
    if (any_of(row.begin(), row.end(), [](int x) { return x != 0; })) {
        int count = count_if(row.begin(), row.end(), [](int x) { return x == 0; });
        return make_pair(count, row.size() - count);
    } else {
        return make_pair(row.size(), 0);
    }
}

vector<vector<int>> reduce_subpatterns(vector<vector<int>>& matrix) {
    matrix = remove_zero_rows(matrix);
    size_t i = 0;
    while (i < matrix.size()) {
        size_t j = i + 1;
        while (j < matrix.size()) {
            if (is_subpattern(matrix[j], matrix[i])) {
                matrix.erase(matrix.begin() + i);
                i--;
                break;
            } else if (is_subpattern(matrix[i], matrix[j])) {
                matrix.erase(matrix.begin() + j);
                j--;
            }
            j++;
        }
        i++;
    }
    return matrix;
}

int kth_nonzero_index(const vector<int>& lst, int k) {
    vector<int> non_zero_list;
    for (size_t i = 0; i < lst.size(); ++i) {
        if (lst[i] != 0) {
            non_zero_list.push_back(i);
        }
    }
    if (non_zero_list.size() < static_cast<size_t>(k)) {
        return -1; // k is larger than the number of non-zero values in lst
    }
    return non_zero_list[k - 1];
}
