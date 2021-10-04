import random

def sqrt_mod_p(n, p):
	def is_residue(x):
		return pow(x, (p - 1) // 2, p) == 1

	while True:
		a = random.randint(1, p - 1)
		if not is_residue((a * a - n) % p):
			break

	def mul(x, y):
		return ((x[0] * y[0] + x[1] * y[1] * (a * a - n)) % p, (x[0] * y[1] + x[1] * y[0]) % p)

	def exp(x, n):
		ret = (1, 0)
		while n:
			if n & 1:
				ret = mul(ret, x)
			n >>= 1
			x = mul(x, x)
		return ret

	return exp((a, 1), (p + 1) // 2)[0]