class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

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
		raise NotImplementedError

	def mul(self, A, n):
		assert isinstance(A, Point) and isinstance(B, int), "Curve can only multiple a point by an integer"
		raise NotImplementedError

def SmartAttack(curve: EllipticCurve, Q: Point, P: Point) -> int:
	raise NotImplementedError



