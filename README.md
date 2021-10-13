# Common Crypto Algorithm Library

## Introduction

Some code that I don't want to write everytime I see relevant challenges.

## Algorithm List

### Lattice

This part is implemented using fpylll library.

#### LLL

Pass in a simple 2D int array, return the result as a 2D int array.

#### coppersmith

Not implemented yet.

#### multivariable coppersmith

Not implemented yet.

#### CVP in $\mathbb{Z_p}$

Not implemented yet.

### Number Theory

#### Chinese Remainder Theorem

Given a list of 2-tuple of the form (mod, remainder), perform crt and return the result in the same 2-tuple format. The moduli can be not pairwise-coprime, but if there's no solution, a `(-1, -1)` is returned.

```python
crt(ls: list) -> tuple
```

#### sqrt mod p

It is implemented using [Cipolla's algorithm](https://en.wikipedia.org/wiki/Cipolla%27s_algorithm). Precondition: `n` is a quadratic residue of `p`.

```python
sqrt_mod_p(n: int, p: int) -> int
```

#### Solve quadratic equation mod p

Solve a quadratic equation mod p and return the roots as a list.

```python
solve_quadratic_mod_p(a: int, b; int, c: int, p: int) -> List
```

#### Pohlig Hellman

With factordb API, first create a `PohligHellman` class by passing in the prime `p` with optional factorization of `(p-1)`. Then the `get_discrete_log` function can solve the discrete log problem.

### RSA

#### Wiener Attack

Given the public key, return `p`, `q`, and `d` in the order.

```python
wiener_attack(N: int, e: int)
```

#### Boneh Durfee Attack

Not implemented yet.

### ECC

#### Smart Attack

Not implemented yet.

#### MOV Attack

Not implemented yet.

### Misc

#### Create a pseudo prime that pass Miller Rabin

The source code is provided. Future work: automate the process of choosing the correct parameters.
