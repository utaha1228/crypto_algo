import decimal

def wiener_attack(N: int, e: int):
	upp = [1, 0]
	low = [0, 1]
	a = N
	b = e
	while True:
		a, b = b, a
		tmp = b // a
		upp.append(upp[-2] + upp[-1] * tmp)
		low.append(low[-2] + low[-1] * tmp)
		b -= a * tmp
		if b == 0:
			break

	for d, k in zip(low, upp):
		if k == 0 or (e * d - 1) % k:
			continue
		phi = (e * d - 1) // k
		PLUS = N + 1 - phi
		MINUS = int(decimal.Decimal(PLUS * PLUS - 4 * N) ** (1 / decimal.Decimal(2)))
		if (MINUS + PLUS) & 1:
			MINUS += 1
		p = (PLUS + MINUS) // 2
		q = PLUS - p
		if p * q == N:
			return p, q, d

	print("Failed to perform Wiener Attack.")
	return

def boneh_durfee_attack(N: int, e: int):
	# https://github.com/mimoo/RSA-and-LLL-attacks/blob/master/boneh_durfee.sage