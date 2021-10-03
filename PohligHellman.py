import math
from factordb.factordb import FactorDB

class PohligHellman:
	def __init__(self, p, fac = None):
		self.p = p
		if fac :
			self.fac = fac
		else:
			try:
				f = FactorDB(p - 1)
				f.connect()
				tmp = f.get_factor_from_api()
				self.fac = [(int(x[0]), x[1]) for x in tmp]
			except:
				print("Cannot factor (p - 1).")
				raise

	def is_primitive_root(self, g):
		for q, e in self.fac:
				if pow(g, (self.p - 1) // q, self.p) == 1:
					flag = False
					return False
		return True

	def get_primitive_root(self):
		g = 1
		while not self.is_primitive_root(g):
			g += 1	
		return g

	def get_discrete_log(self, x, g=None, debug=False):
		if g == None:
			try:
				g = self.smallest_primitive_root
			except:
				self.smallest_primitive_root = self.get_primitive_root()
				g = self.smallest_primitive_root

		rem = []
		p = self.p
		for q, e in self.fac:
			if debug:
				print(q, e)
			b = pow(g, (p - 1) // q, p)
			sq = int(math.sqrt(q)) + 1
			small_step = [1]
			big_step_dict = {}
			for i in range(1, sq):
				small_step.append(small_step[-1] * b % p)
			big_base = small_step[-1] * b % p
			pre = 1
			for i in range(sq):
				big_step_dict[pre] = i
				pre = pre * big_base % p

			def find(u):
				for i, x in enumerate(small_step):
					y = u * pow(x, -1, p) % p
					if y in big_step_dict:
						return (big_step_dict[y] * sq + i) % q
				print(f"Cannot find discrete log when q = {q}")
				raise

			r = 0
			_x = x
			pw = 1
			for i in range(e):
				tmp = find(pow(_x, (p - 1) // pw // q, p))
				r += pw * tmp
				_x = _x * pow(g, -tmp * pw, p) % p
				pw = pw * q

			rem.append((pw, r))
		if debug: 
			print(rem)
		ans = 0
		for q, r in rem:
			coe = r * pow((p - 1) // q, -1, q)
			ans += coe * (p - 1) // q

		ans %= (p - 1)
		return ans
