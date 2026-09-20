from sage.all import GF, ZZ, randint, gcd, inverse_mod, is_prime, randrange, is_pseudoprime, prime_range

def is_prime_basic(p, q, primes):
    """
    Performs trial division on p and q simultaneously to quickly rule out the possibility of p = 2q + 1 being prime.
    Inputs:
        p (int): Candidate safe prime.
        q (int): Candidate Sophie Germain prime.
        primes (list): List of small primes for trial division.
    Returns:
        bool: False if p or q is divisible by any small prime; otherwise True.
    """
    for prime in primes:
        if prime == p or prime == q:
            continue
        if q % prime == 0 or p % prime == 0:
            return False
    return True


def generate_safe_prime(bit_length):
    """
    Generates safe primes of desired bit length efficiently by checking for primality with incremental strictness.
    Inputs:
        bit_length (int): The desired bit length of the safe prime p.
    Returns:
        p, q (tuple): A safe prime p and its Sophie Germain prime q.
    """
    primes = prime_range(10000)
    while True:
        q = randrange(2**(bit_length - 2), 2**(bit_length - 1))
        p = 2 * q + 1
        
        if is_prime_basic(p, q, primes): # Test 1
            if is_pseudoprime(p) and is_pseudoprime(q): # Test 2
                if is_prime(p) and is_prime(q): # Test 3
                    return p, q


def generate_public_parameters(p, q, reduced):
    '''
    Inputs:
        p (int): Prime p
        q (int): Prime q, divisor of p - 1
        reduced (bool) : Whether to reduce generator g to order q
    Returns:
        g (int): Generator g either of order p - 1 or q. 
    '''
    P = GF(p)
    g = P.multiplicative_generator()
    if reduced:
        g = g ** ((p - 1) // q)
    return int(g)


def elgamal_keygen(p, g):
    """
    Generate ElGamal key pair.
    Inputs:
        p (int): Prime modulus
        g (int): Generator of Z/pZ
    Returns:
        sk (int): The private key (random in p).
        pk (int): The public key (g^sk mod p).
    """
    sk = randint(0, p - 1)
    pk = pow(g, sk, p)
    return (sk, pk)


def elgamal_sign(p, g, m, sk):
    """
    Sign a message using the ElGamal digital signature scheme.
    Parameters:
        p (int): Prime Modulus
        g (int): Generator of Z/pZ
        m (int): Message to be signed.
        sk (int): Private key for signing.
    Returns:
        r (int): g^k mod p, for random k.
        s (int): Computed using k, sk, and m.
    """
    # Finds random k such that k is invertible mod p-1
    k = randint(0, p - 1)
    while gcd(k, p - 1) != 1:
        k = randint(0, p - 1)

    k_inv = inverse_mod(k, p - 1) # Computes inverse

    r = pow(g, k, p) # Computes r
    sig = (k_inv * (m - (sk  * ZZ(r)))) % (p - 1) # Computes sig

    return (r, sig)


def elgamal_verify(p, g, m, pk, signature):
    """
    Verify an ElGamal signature.
    Parameters:
        p (int): Prime Modulus
        g (int): Generator of Z/pZ
        m (int): Message for signature verification.
        pk (int): Public key of message signer.
        signature (tuple): Signature (r, s) to verify.
    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    # Checks g^m = pk^r * r^sig (mod p)
    r, sig = signature
    lhs = pow(g, m, p)
    rhs = (pow(pk, r, p) * pow(r, sig, p)) % p
    return lhs == rhs


def main():
    p, q = generate_safe_prime(1024) # Safe prime p = 2q + 1
    g = generate_public_parameters(p, q, True) # Public parameters
    m = randint(1, p - 1) # Message to be signed

    sk_Alice, pk_Alice = elgamal_keygen(p, g) # Alice's keys
    signature_Alice = elgamal_sign(p, g, m, sk_Alice) # Alice's signature for message m

    sk_Bob, pk_Bob = elgamal_keygen(p, g) # Bob's keys
    signature_Bob = elgamal_sign(p, g, m, sk_Bob) # Bob's signature for message m

    print(elgamal_verify(p, g, m, pk_Alice, signature_Alice)) # Valid
    print(elgamal_verify(p, g, m, pk_Bob, signature_Bob)) # Valid

    print(elgamal_verify(p, g, m, pk_Alice, signature_Bob)) # Invalid
    print(elgamal_verify(p, g, m, pk_Bob, signature_Alice)) # Invalid


if __name__ == '__main__':
    main()