from fpylll import *
from math import ceil, floor, log10
import numpy as np
import decimal

def lll(matrix):
	A = IntegerMatrix.from_matrix(matrix)
	ret = [[0] * len(matrix[0]) for _ in range(len(matrix))]
	LLL.reduction(A).to_matrix(ret)
	return ret

# from https://github.com/mimoo/RSA-and-LLL-attacks/blob/master/coppersmith.sage 
# Find the small root of polynomial `poly` modulo `p`, a factor of `mod`. 
# precondition:
# 	p <= pow(N, beta)
#	the small root <= pow(N, beta * beta / deg - epsilon)
#
# debug: provides more useful output if true
# prec, iteration: parameter for Newton's root finding method
def coppersmith(poly, N, beta, epsilon, debug=False, prec=1000, iteration=100):
	decimal.getcontext().prec = prec
	assert prec > N.bit_length() * math.log10(2)
	assert poly[-1] == 1, "the polynomial has to be monic"
	deg = len(poly) - 1
	assert epsilon <= beta / 7
	h = int(ceil(beta * beta / (deg * epsilon)))
	t = int(floor(deg * h * ((1 / beta) - 1)))
	
	upper_bound = int(decimal.Decimal(N) ** decimal.Decimal(beta * beta / deg - epsilon))

	if debug:
		print(f'Upper bound of the root = {upper_bound}')

	matrix_size = deg * h + t

	matrix = [[] for _ in range(matrix_size)]


	# filling in the coefficient
	cur_poly = [N ** h]
	for i in range(h):
		# here cur_poly = (N ** (h-i)) * (poly ** i)
		for j in range(deg):
			matrix[i * deg + j] = [0] * j + cur_poly
			while len(matrix[i * deg + j]) < matrix_size:
				matrix[i * deg + j].append(0)

		#update cur_poly for the next iteration
		cur_poly = [x // N for x in cur_poly]
		next_poly = [0] * (len(cur_poly) + deg)
		for _i in range(deg + 1):
			for _j in range(len(cur_poly)):
				next_poly[_i + _j] += cur_poly[_j] * poly[_i]

		cur_poly = next_poly
	for i in range(t):
		matrix[h * deg + i] = [0] * i + cur_poly
		while len(matrix[h * deg + i]) < matrix_size:
			matrix[h * deg + i].append(0)

	if debug:
		for i in range(matrix_size):
			print(' '.join(['.' if x == 0 else 'X' for x in matrix[i]]))

	# plug in `upper_bound`
	for i in range(matrix_size):
		for j in range(matrix_size):
			matrix[i][j] *= (upper_bound ** j)

	res = lll(matrix)[0]
	res = [x // (upper_bound ** i) for i, x in enumerate(res)]
	derivated_res = [x * i for i, x in enumerate(res)][1:]

	res = res[::-1]
	derivated_res = derivated_res[::-1]

	# find root of polynomial constructed by `res`, specifically, res[0] * x^d + ... + res[-1]
	ans = []
	eps = 1e-5

	def poly_eval(P, x):
		tmp = 0
		for c in P:
			tmp = tmp * x + c
		return tmp

	def is_root(P, x):
		return poly_eval(P, x) == 0

	for root in np.roots(res):
		if abs(root.imag) > eps:
			continue
		curX = decimal.Decimal(root.real)
		for _ in range(iteration):
			curX = curX - poly_eval(res, curX) / poly_eval(derivated_res, curX)

		rt = int(curX)
		for delta in range(-10, 10):
			if is_root(res, rt + delta):
				ans.append(rt + delta)
	return ans

from Crypto.Util.number import *
import random
def test():
	p = getPrime(512)
	q = getPrime(512)
	if p < q:
		p, q = q, p
	N = p * q
	root = random.randint(1, int(p ** 0.1))
	a = 1
	b = random.randint(1, N)
	c = (- a * root * root + -b * root) % p
	poly = [c, b, a]
	assert (a * root * root + b * root + c) % p == 0
	print(root)
	print(coppersmith(poly, N, 0.5, 0.5 / 7, True))


test()

