"""GF(2^10) construction and a Diffie-Hellman exchange demo inside it.

Prime fields are generally preferred over small-characteristic fields like
F_{2^n} for real cryptographic use, since index calculus is more effective
against the latter -- this module exists to demonstrate the field/group
mechanics, not as a parameterization recommendation.
"""

from sage.all import GF, SR, randint

# Prime power for finite field
q = 2**10
# Defining polynomial for finite field of q
x = SR.var('x')
f = x**10 + x**9 + x**8 + x**7 + x**6 + x**5 + x**4 + x**3 + x**2 + x + 1

# Initialize finite field with generator x
Q = GF(q, 'x', f)
x = Q.gen()

g = Q(1 + x**3 + x**4 + x**5 + x**9) # Construct element g(x) in Q


def generate_DH_keys():
    """
    Generate Diffie-Hellman key pair.
    Returns:
        sk (int): Secret key, random integer in q
        pk (int): Public key, g^sk (mod q)
    """
    sk = randint(1, q - 2)
    pk = g ** sk
    return sk, pk


def compute_shared_secret(sk, pk):
    """
    Computes Diffie-Hellman shared secret.
    Returns:
        ss (int): Shared secret key, pk^sk (mod q)
    """
    return pk ** sk


def main():
    """Demo: two parties derive the same shared secret via g in GF(2^10)."""
    print(f'Order of g: {g.multiplicative_order()}')

    sk_diffie, pk_diffie = generate_DH_keys()
    sk_hellman, pk_hellman = generate_DH_keys()

    ss_diffie = compute_shared_secret(sk_diffie, pk_hellman)
    ss_hellman = compute_shared_secret(sk_hellman, pk_diffie)

    print(ss_diffie == ss_hellman)


if __name__ == '__main__':
    main()