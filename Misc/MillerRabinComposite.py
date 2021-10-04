from Crypto.Util.number import isPrime
import random
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61]

k2 = 97
k3 = 241

res = []
for p in primes:
    if p == 2:
        assert k2 % 8 == 1
        assert k3 % 8 == 1
        res.append((3, 8))
    else:
        qr = set({})
        for i in range((p + 1) // 2):
            qr.add(i * i % p)

        rem = -1
        
        if p % 4 == 1:
            for i in range(1, p):
                if (i not in qr) and ((k2 * (i - 1) + 1) % p not in qr) and ((k3 * (i - 1) + 1) % p not in qr):
                    rem = i
                    break
        else:
            rem = 1

        if rem == -1:
            print(f"oops for p = {p}")
            exit(0)

        res.append((rem, p))

res.append((-pow(k3, -1, k2) % k2, k2))
res.append((-pow(k2, -1, k3) % k3, k3))
print(res)

rem = 0
mod = 1
for r, q in res:
    rem = (rem + (r - rem) * pow(mod, -1, q) * mod) % (mod * q)
    mod *= q

print(rem, mod)

for i in range(10000):
    x = random.randint(1 << 108, 1 << 109)
    p1 = x * mod + rem
    p2 = k2 * (p1 - 1) + 1
    p3 = k3 * (p1 - 1) + 1
    if isPrime(p1) and isPrime(p2) and isPrime(p3):
        print(p1)
        print(p2)
        print(p3)
        exit(0)

'''
p1 = 5114931177751823607820031739043210074217385809731311886407107
p2 = 496148324241926889958543078687191377199086423543937252981489283
p3 = 1232698413838189489484627649109413627886389980145246164624112547
'''
