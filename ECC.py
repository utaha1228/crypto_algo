class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __str__(self):
		return f'({self.x}, {self.y})'

Point.O = Point(-1, -1)

class EllipticCurve:
	def __init__(self, p, a, b, order=None):
		self.p = p
		self.a = a
		self.b = b
		self.order = order

	def isOnCurve(self, A):
		return A == Point.O or (A.x * A.x * A.x + self.a * A.x + self.b - A.y * A.y) % p == 0

	def inv(self, A):
		return Point(-A.x % p, A.y)

	def add(self, A, B):
		assert isinstance(A, Point) and isinstance(B, Point), "Curve can only add two points"
		if A == Point.O:
			return Point(B.x, B.y)
		elif B == Point.O:
			return Point(A.x, A.y)
		elif (A.y + B.y) % self.p == 0 and A.x == B.x:
			return Point(Point.O.x, Point.O.y)
		else:
			lmbda = (self.a + 3 * A.x * A.x) * pow(2 * A.y, -1, self.p) if A.x == B.x else (B.y - A.y) * pow(B.x - A.x, -1, self.p) % p
			x = (lmbda * lmbda - A.x - B.x) % p
			y = (lmbda * (A.x - x) - A.y) % p
			return Point(x, y)

	def mul(self, A, n):
		assert isinstance(A, Point) and isinstance(n, int), "Curve can only multiple a point by an integer"
		res = Point.O
		while n:
			if n & 1:
				res = self.add(res, A)
			A = self.add(A, A)
			n >>= 1
		return res

def SmartAttack(curve: EllipticCurve, Q: Point, P: Point) -> int:
	raise NotImplementedError



