from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes, bytes_to_long

class GF128Element:
	def __init__(self, value: int=0):
		# the MSB is the coefficient of x^0
		self.val = value

	@staticmethod
	def from_bytes(block: bytes):
		assert len(block) <= 16
		return GF128Element(bytes_to_long(block))

	def to_bytes(self) -> bytes:
		return long_to_bytes(self.val, 16)

	def __add__(self, x):
		assert isinstance(x, GF128Element), "Cannot add GF128Element with other type"
		return GF128Element(self.val ^ x.val)

	def __mul__(self, x):
		assert isinstance(x, GF128Element), "Cannot multiple GF128Element with other type"
		res = 0
		x = x.val
		for i in range(127, -1, -1):
			res ^= x * ((self.val >> i) & 1)
			x = (x >> 1) ^ ((x & 1) * 0xE1000000000000000000000000000000)
		return GF128Element(res)

	def __pow__(self, b):
		assert isinstance(b, int), "GF128Element only support integer exponent"
		res = GF128Element(1 << 127) # res = x^0
		a = GF128Element(self.val)
		while b:
			if b & 1:
				res = res * a
			a = a * a
			b >>= 1
		return res

	def inv(self):
		return self ** ((1 << 128) - 2)

	def get_coefficient(idx: int) -> int:
		assert 0 <= idx and idx < 128, "Index out of range" # 0-index
		return (self.val >> (127 - idx)) & 1

class GCM:
	def __init__(self, key: bytes, nonce: bytes):
		self.key = key
		cipher = AES.new(key, AES.MODE_ECB)
		self.H = GF128Element.from_bytes(cipher.encrypt(b'\x00' * 16))
		self.nonce = nonce
		if len(nonce) == 12:
			nonce += b'\x00\x00\x00\x01'
		else:
			nonce_len_block = long_to_bytes(len(nonce) * 8, 16)
			nonce += b'\x00' * (-len(nonce) % 16)
			nonce = GCM.ghash(self.H, nonce + nonce_len_block)
		self.mask = cipher.encrypt(nonce)

	@staticmethod
	def get_hash_string(msg: bytes, authdata: bytes=b'') -> bytes:
		msg_length = len(msg) * 8
		ad_length = len(authdata) * 8
		if len(msg) % 16:
			msg += b'\x00' * (16 - len(msg) % 16)
		if len(authdata) % 16:
			authdata += b'\x00' * (16 - len(authdata) % 16)
		return authdata + msg + long_to_bytes((ad_length << 64) ^ msg_length, 16)

	@staticmethod
	def ghash(H: GF128Element, s: bytes) -> bytes:
		assert len(s) % 16 == 0, "Length must be a multiple of 16"
		ret = GF128Element(0)
		for i in range(0, len(s), 16):
			block = GF128Element.from_bytes(s[i: i + 16])
			ret = block + ret * H
		ret = ret * H
		return ret.to_bytes()

	def get_tag(self, ciphertext: bytes, authdata: bytes=b'') -> bytes:
		s = GCM.ghash(self.H, GCM.get_hash_string(ciphertext, authdata))
		s = bytes([x ^ y for x, y in zip(s, self.mask)])
		return s


###### Testing ######

# a = GF128Element(0xcafedeadbeef)
# b = a.inv()
# print((a * b).val)
# print((1 << 127))

# master_key = bytes.fromhex('feffe9928665731c6d6a8f9467308308')
# plaintext = bytes.fromhex('d9313225f88406e5a55909c5aff5269a86a7a9531534f7da2e4c303d8a318a721c3c0c95956809532fcf0e2449a6b525b16aedf5aa0de657ba637b39')
# auth_data = bytes.fromhex('feedfacedeadbeeffeedfacedeadbeefabaddad2')
# init_value = bytes.fromhex('9313225df88455909c5aff5269aa6a7a9538534f7da1e4c303d2a318a728c3c0c95156809539fcf0e2429a6b525416aedbf5a0de6a57a637b39b')

# gcm = GCM(master_key, init_value)

# aes = AES.new(master_key, AES.MODE_GCM, nonce=init_value)
# aes.update(auth_data)
# ct, tag = aes.encrypt_and_digest(plaintext)

# print(f'ct = {ct.hex()}')
# print(f'my tag: {gcm.get_tag(ct, authdata=auth_data).hex()}')
# print(f'real tag: {tag.hex()}')
