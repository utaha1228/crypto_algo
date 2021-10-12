from fpylll import *

def LLL(matrix):
	A = IntegerMatrix.from_matrix(matrix)
	ret = [[0] * len(matrix[0]) for _ in range(len(matrix))]
	LLL.reduction(A).to_matrix(ret)
	return ret
