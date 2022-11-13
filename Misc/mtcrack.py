from typing import List
from tqdm import tqdm

class Mt19937:
	w, n, m, r = (32, 624, 397, 31)
	a = 0x9908B0DF
	u, d = (11, 0xFFFFFFFF)
	s, b = (7, 0x9D2C5680)
	t, c = (15, 0xEFC60000)
	l = 18
	mask = (1 << w) - 1
	lowerMask = (1 << r) - 1
	upperMask = mask ^ lowerMask
	f = 1812433253
	def __init__(self):
		self.state = [None] * Mt19937.n
		self.index = Mt19937.n

	def _init_genrand(self, seed):
		xor_shift = lambda x: x ^ (x >> 30)
		self.state[0] = seed
		for i in range(1, Mt19937.n):
			self.state[i] = (1812433253 * xor_shift(self.state[i - 1]) + i) & Mt19937.mask
		self.index = Mt19937.n

	def _init_by_array(self, key):
		xor_shift = lambda x: x ^ (x >> 30)
		self._init_genrand(19650218)

		i, j = 1, 0
		k = max(Mt19937.n, len(key))
		while k > 0:
			self.state[i] = (self.state[i] ^ (xor_shift(self.state[i - 1]) * 1664525)) + key[j] + j
			self.state[i] &= Mt19937.mask
			i += 1
			j += 1

			if i >= Mt19937.n:
				self.state[0] = self.state[Mt19937.n - 1]
				i = 1
			if j >= len(key):
				j = 0

			k -= 1
		k = Mt19937.n - 1
		while k > 0:
			k -= 1
			self.state[i] = (self.state[i] ^ (xor_shift(self.state[i - 1]) * 1566083941)) - i
			self.state[i] &= Mt19937.mask
			i += 1
			if i >= Mt19937.n:
				self.state[0] = self.state[Mt19937.n - 1]
				i = 1
		self.state[0] = 0x80000000

	def seed(self, seed: int, version: str = "python"):
		if version == "c":
			self.state = [seed]
			for i in range(1, self.n):
				self.state.append(Mt19937.mask & (i + Mt19937.f * (self.state[i-1] ^ (self.state[i-1] >> (self.w - 2)))))

		elif version == "python":
			key = []
			while seed:
				key.append(seed & Mt19937.mask)
				seed >>= Mt19937.w
			self._init_by_array(key)

	def temper(self, num: int) -> int:
		num = num ^ ((num >> Mt19937.u) & Mt19937.d)
		num = num ^ ((num << Mt19937.s) & Mt19937.b)
		num = num ^ ((num << Mt19937.t) & Mt19937.c)
		num = num ^ (num >> Mt19937.l)
		return num
		
	def rand(self) -> int:
		if self.index >= Mt19937.n:
			self.twist()
		y = self.state[self.index]
		self.index += 1
		return self.temper(y)

	def twist(self) -> None:
		for i in range(Mt19937.n):
			x = (self.state[i] & Mt19937.upperMask) ^ (self.state[(i + 1) % Mt19937.n] & Mt19937.lowerMask)
			xA = x >> 1
			if x & 1:
				xA = xA ^ Mt19937.a

			self.state[i] = self.state[(i + Mt19937.m) % Mt19937.n] ^ xA

		self.index = 0

class LinearBase:
	"""
	Solver for linear equaion system in GF(2)
	"""
	def __init__(self, n):
		self.n = n
		self.lb = [None for _ in range(n)]
		self.n_equations = 0

	def isFull(self) -> bool:
		return self.n_equations == self.n

	def add(self, mask: int, value: int) -> None:
		for i in range(self.n):
			if mask & (1 << i):
				if self.lb[i] == None:
					self.lb[i] = [mask, value]
					self.n_equations += 1
					return
				else:
					mask ^= self.lb[i][0]
					value ^= self.lb[i][1]
		assert mask == 0, "No way... maybe the mask has more than `n` bits?"
		assert not value, "Conflicting equation"

	def solve(self) -> List[bool]:
		assert self.isFull(), "Solution not unique"
		sol = []
		for i in tqdm(range(self.n)):
			for j in range(i + 1, self.n):
				if self.lb[i][0] & (1 << j):
					self.lb[i][0] ^= self.lb[j][0]
					self.lb[i][1] ^= self.lb[j][1]
			sol.append(self.lb[i][1])
		return sol


class MtCracker:
	"""
	The state have 624 32-bit integers, but the lower 31 bits of state[0] is not used after the twist.
	Therefore, the recovered state will miss those 31 bits.

	A state is represented by an array of 32 "bitmask", and the first element of the array is the LSB.
	"""
	def __init__(self):
		self.solver = LinearBase((Mt19937.n - 1) * Mt19937.w + 1)
		self.cache = []
		self.index = Mt19937.n
		self.state = []
		pt = 0
		for i in range(Mt19937.n):
			state = []
			for j in range(Mt19937.w):
				if i == 0 and j < Mt19937.w - 1:
					state.append(0)
				else:
					state.append(1 << pt)
					pt += 1
			self.state.append(state)

	def temper(self, num: List[int]) -> List[int]:
		num = num[:]
		# num = num ^ ((num >> Mt19937.u) & Mt19937.d)
		xorTo = [num[i + Mt19937.u] if i + Mt19937.u < Mt19937.w and ((Mt19937.d >> i) & 1) else 0 for i in range(Mt19937.w)]
		num = [x ^ y for x, y in zip(num, xorTo)]
		
		# num = num ^ ((num << Mt19937.s) & Mt19937.b)
		xorTo = [num[i - Mt19937.s] if i - Mt19937.s >= 0 and ((Mt19937.b >> i) & 1) else 0 for i in range(Mt19937.w)]
		num = [x ^ y for x, y in zip(num, xorTo)]
		
		# num = num ^ ((num << Mt19937.t) & Mt19937.c)
		xorTo = [num[i - Mt19937.t] if i + Mt19937.t >= 0 and ((Mt19937.c >> i) & 1) else 0 for i in range(Mt19937.w)]
		num = [x ^ y for x, y in zip(num, xorTo)]
		
		# num = num ^ (num >> Mt19937.l)
		xorTo = [num[i + Mt19937.l] if i + Mt19937.l < Mt19937.w else 0 for i in range(Mt19937.w)]
		num = [x ^ y for x, y in zip(num, xorTo)]

		return num
		
	def rand(self) -> List[int]:
		if self.index >= Mt19937.n:
			self.twist()
		y = self.state[self.index].copy()
		self.index += 1
		return self.temper(y)

	def twist(self) -> None:
		for i in range(Mt19937.n):
			x = self.state[(i + 1) % Mt19937.n][:Mt19937.r]\
				+ self.state[i][Mt19937.r:]
			xA = x[1:] + [0]
			xA = [xA[i] ^ x[0] if (Mt19937.a & (1 << i)) else xA[i] for i in range(Mt19937.w)]

			self.state[i] = [x ^ y for x, y in zip(self.state[(i + Mt19937.m) % Mt19937.n], xA)]

		self.index = 0

	def isFull(self) -> bool:
		return self.solver.isFull()

	def update(self, pos: int, bit_pos: int, value: bool) -> None:
		"""
		Both `pos`, `bit_pos` is 0-indexed, and smaller `bit_pos` corresponds to LSB.
		"""
		while len(self.cache) <= pos:
			self.cache.append(self.rand())

		self.solver.add(self.cache[pos][bit_pos], value)

	def solve(self) -> List[int]:
		bits = self.solver.solve()
		ret = [bits[0] << (Mt19937.w - 1)]
		bits = bits[1:]
		# from LSB to MSB
		for i in range(0, len(bits), Mt19937.w):
			_ = "".join("1" if x else "0" for x in bits[i : i + Mt19937.w])
			ret.append(int(_[::-1], 2))
		return ret

""" testing """
if __name__ == "__main__":
	import random

	# test seeding
	seed = 0x8787948787638763
	random.seed(seed)
	mt = Mt19937()
	mt.seed(seed)
	assert random.getrandbits(32) == mt.rand()

	# test mtcrack
	LEN = 650
	assert LEN >= Mt19937.n
	crack = MtCracker()
	random.seed(0x87878787)
	output = [random.getrandbits(32) for _ in range(LEN)]

	for pos in tqdm(range(LEN)):
		for bit_pos in range(32):
			crack.update(pos, bit_pos, (output[pos] >> bit_pos) & 1)

	initial_state = crack.solve()
	rng = Mt19937()
	rng.state = initial_state
	assert [rng.rand() for _ in range(LEN)] == output

