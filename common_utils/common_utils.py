import os
import sys

def getwt(directory, filename):
    f = open(os.path.join(directory, filename), "r")
    matrix = []
    for line in f:
      row = [int(x) for x in line.split()]
      matrix.append(row)
      #print(f"Dimensions: {len(matrix)} x {len(matrix[0])}")
    return matrix

def rename_files(directory):
    files = sorted(os.listdir(directory))
    for i, file in enumerate(files):
        new_name = f"layer{i:02 + 1}.txt"
        os.rename(os.path.join(directory, file), os.path.join(directory, new_name))

def read_files(directory):
    directory = os.path.join("../common_utils", directory)
    files = sorted(os.listdir(directory))
    dircontent = []
    for i, file in enumerate(files):
        i += 1
        temp = getwt(directory, f"layer{i:02}.txt")
        dircontent.append(temp)
    return dircontent 

def get_R50():
    activation_matrices = read_files("r50act/")
    weight_matrices = read_files("r50weights/")
    return weight_matrices, activation_matrices
