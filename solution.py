from Crypto.Util.number import bytes_to_long
from pkcs1 import emsa_pkcs1_v15
import json
import math
from pwn import *

r = remote('socket.cryptohack.org', 13391)
r.recvline()

def get_sig():
	r.sendline('{"option":"get_signature"}')
	data = json.loads(r.recvline())
	return int(data['signature'], 16)

msg = b'I am Mallory.own CryptoHack.org'
m = emsa_pkcs1_v15.encode(msg, 256)
m = bytes_to_long(m)
sig = get_sig()


MAXN = 16000
isp = [1] * MAXN
primes = []

for p in range(2, MAXN):
	if isp[p] == 1:
		primes.append(p)
		for i in range(p + p, MAXN, p):
			isp[i] = 0
		if sig % p == 0:
			continue

# Result of Chinese Remainder Theorem
remainder = 0
mod = 1

N = 1
for p in primes:
	# print the progress. When N > m, which means N is roughly 2048 bits long, then we are done.
	# print(f"p = {p}")
	# print(f"Bit length of N = {N.bit_length()}")

	# since p is small, we can find the discrete log by brute forcing.
	order = -1
	lg = -1
	cur = 1
	for i in range(p):
		if cur == 1 and i != 0:
			order = i
			break
		if cur == m % p:
			assert lg == -1
			lg = i
		cur = cur * sig % p

	# no discrete log found. skip this prime.
	if lg == -1 or order == -1:
		continue

	# combine CRT result. Similarly, we can brute force since the order is smaller than the p.
	# the old equation is e = remainder (mod mod)
	# the new equation is e = lg (mod order)
	newR = remainder
	for i in range(order):
		if newR % order == lg:
			break
		newR += mod

	# no solution for CRT. skip this prime.
	if newR % order != lg:
		continue

	remainder = newR
	mod = order * mod // math.gcd(order, mod)
	N *= p
	if N >= m:
		break


e = remainder
print(f"Bit length of N = {N.bit_length()}")
print(f"N = {N}")
print(f"Bit length of e = {e.bit_length()}")
print(f"e = {e}")

def get_flag(n, e):
	json_payload = {"option":"verify","N":hex(n),"e":hex(e),"msg":"I am Mallory.own CryptoHack.org"}
	tmp = str(json.dumps(json_payload))
	tmp.replace(' ', '') # reduce payload size by removing space
	print(f"Payload length is {len(tmp)}")
	r = remote('socket.cryptohack.org', 13391)
	r.recvline()
	r.send(tmp)
	s = r.recvline()
	print(s)

get_flag(N, e)

