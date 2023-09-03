# credit to maple3142
# https://blog.maple3142.net/2023/06/12/seetf-2023-writeups/#shard

def flatter(M):
	from re import findall
	from subprocess import check_output
	z = "[[" + "]\n[".join(" ".join(map(str, row)) for row in M) + "]]"
	ret = check_output(["flatter"], input=z.encode())
	return matrix(M.nrows(), M.ncols(), map(int, findall(b"-?\\d+", ret)))

def small_roots(f, X, beta=1.0, m=None):
	N = f.parent().characteristic()
	delta = f.degree()
	if m is None:
		epsilon = RR(beta^2/f.degree() - log(2*X, N))
		m = max(beta**2/(delta * epsilon), 7*beta/delta).ceil()
	t = int((delta*m*(1/beta - 1)).floor())
	
	f = f.monic().change_ring(ZZ)
	P,(x,) = f.parent().objgens()
	g  = [x**j * N**(m-i) * f**i for i in range(m) for j in range(delta)]
	g.extend([x**i * f**m for i in range(t)]) 
	B = Matrix(ZZ, len(g), delta*m + max(delta,t))

	for i in range(B.nrows()):
		for j in range(g[i].degree()+1):
			B[i,j] = g[i][j]*X**j

	B = flatter(B)
	f = sum([ZZ(B[0,i]//X**i)*x**i for i in range(B.ncols())])
	roots = set([f.base_ring()(r) for r,m in f.roots() if abs(r) <= X])
	return [root for root in roots if N.gcd(ZZ(f(root))) >= N**beta]

if __name__ == "__main__":
	import time
	import math
	n = 24712135189687942739677490021030751776088469214818275631687482073531676912880823269667196936095460153002434759403063429337125873794523587731746689517070810687221399532024093572951282737818446579992570629531618780373767724789390101166147862982539311016801595612323156816999866783427829783286164172896802725820761659256555627406518829192800217880692359914672894220547306033679060066475600137205045054015651689487444267401130160872050085589597109014374199731072611044277806027332254214020499883131062627540945260814416104971893858787291926267157394988131329441246648393933117451348643609850156730059817506513924523851733
	p = 161405912451824860188834725646055524173328544131300133372580621368926433914138476338787007253318242142454894032713487340762003643551953941809023233323836632396674586164821404065443903169766781702197174899338334027128103867874700640036605974611327518250687560220955598412727224450293311080620976484498655311739
	PR.<x> = PolynomialRing(Zmod(n))
	# modified from https://github.com/Connor-McCartney/Connor-McCartney.github.io/blob/main/_pages/cryptography/small-roots/push-it-to-the-limit-WACON-2023-prequal.md
	m = 1
	for brute in [210 * 11 * 13 * 17, 210 * 11 * 13, 210 * 11, 210]:
		mid = p - p % (1 << 512) + (1 << 511)
		mid = mid // brute * brute
		while True:
			starttime = time.time()
			f = mid + brute * x + p % brute
			X = (1 << 511) // brute
			roots = small_roots(f, X=X, beta=0.5, m=m)
			if roots == []:
				m += 1
				continue
			p = gcd(mid + brute * roots[0] + p % brute, n)
			assert 1 < p < n, str(p)
			t = time.time() - starttime
			phi = sum([1 for i in range(1, brute) if math.gcd(i, brute) == 1])
			print(f"bruting {brute} with m={m}: {phi * t / 3600} hrs")
			break