import math
from factordb.factordb import FactorDB
import random

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


def sqrt_mod_p(n: int, p: int) -> int:
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

def crt(ls: list) -> tuple:
	rem = 0
	mod = 1
	for q, r in ls:
		gcd = math.gcd(q, mod)
		if rem % gcd != r % gcd:
			return (-1, -1)
		rem += mod * ((r - rem) // gcd) * pow(mod // gcd, -1, q // gcd)
		mod = mod * q // gcd
		rem %= mod
	return (mod, rem)
	
def solve_quadratic_mod_p(a: int, b: int, c: int, p: int) -> list:
	D = (b * b - 4 * a * c) % p
	sD = sqrt_mod_p(D, p)
	if sD == -1:
		return []
	elif sD == 0:
		return [-b * pow(2 * a, -1, p) % p]
	else:
		return [(-b + sD) * pow(2 * a, -1, p) % p, (-b - sD) * pow(2 * a, -1, p) % p]

from Crypto.Util.number import sieve_base
import math

def index_calculus(mod: int, a: int, g: int, max_bases: int =100, debug:bool =False):
	# require g to be a primitive root, mod to be a prime
	bases = sieve_base[:max_bases]
	while bases[-1] >= mod:
		bases = bases[:-1]
	max_bases = len(bases)

	equations = [[] for i in range(max_bases)]
	equation_count = 0

	exponent = 0
	_num = 1
	while True:
		exponent += 1
		_num = _num * g % mod

		cnt = [0] * max_bases
		num = _num
		for i, base in enumerate(bases):
			while num % base == 0:
				num //= base
				cnt[i] += 1

		if num != 1:
			continue

		cnt += [exponent]
		for i in range(max_bases):
			if cnt[i] > 0 and len(equations[i]) == 0:
				equations[i] = cnt
				equation_count += 1
				if debug:
					print(f'Found {cnt} = {_num}')
				break

			if cnt[i] == 0:
				continue

			_gcd = math.gcd(cnt[i], equations[i][i]) # cnt <= log_2(mod) --> _gcd <= log_2(mod)
			mul = equations[i][i] // _gcd
			cnt = [x * mul for x in cnt]
			mul = cnt[i] // equations[i][i]
			cnt = [(x - mul * y) % (mod - 1) for x, y in zip(cnt, equations[i])]

		if equation_count == max_bases:
			break

	if debug:
		print("=" * 20)
		for x in equations:
			print(x)
		print("=" * 20)
	for i in range(max_bases - 1, -1, -1):
		for j in range(i + 1, max_bases):
			equations[i][-1] = (equations[i][-1] - equations[i][j] * equations[j][-1]) % (p - 1)
			equations[i][j] = 0
		_gcd = math.gcd(equations[i][i], mod - 1)
		assert equations[i][-1] % _gcd == 0
		sol = (equations[i][-1] // _gcd) * pow(equations[i][i] // _gcd, -1, (mod - 1) // _gcd) % ((mod - 1) // _gcd)
		while pow(g, sol, mod) != bases[i]:
			assert sol < mod
			sol += (mod - 1) // _gcd

		equations[i][i] = 1
		equations[i][-1] = sol

	if debug:
		print("=" * 20)
		for x in equations:
			print(x)
		print("=" * 20)

	addend = 0
	_num = a
	while True:
		cnt = [0] * max_bases
		num = _num
		for i, base in enumerate(bases):
			while num % base == 0:
				num //= base
				cnt[i] += 1

		if num != 1:
			addend += 1
			_num = _num * g % mod
			continue

		return (sum(equations[i][-1] * cnt[i] for i in range(max_bases)) - addend) % (mod - 1)


######## Testing ########

# for i in range(10):
# 	g = 5
# 	p = 97
# 	ans = random.randint(1, p)
# 	assert pow(g, (p - 1) // 2, p) != 1
# 	assert pow(g, (p - 1) // 3, p) != 1
# 	assert index_calculus(p, pow(g, ans, p), g, 5) == ans


