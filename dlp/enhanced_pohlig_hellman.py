from sage.all import GF, factor, crt
from dlp.pollard_rho import pollard_rho

def enhanced_pohlig_hellman(p, g, h):
    """
    Pohlig-Hellman algorithm to solve h = g^x (mod p).
    Enhanced by Pollard's rho algorithm for large prime subgroups.
    Inputs:
        p (int): Prime modulus
        g (int): Generator of Z/pZ
        h (int): Target value
    Returns:
        x (int): Discrete log solution
        None: If no solution is found
    Notes:
        This method assumes the group order is known to be p - 1.
    """

    F = GF(p) # Initialize finite field
    g, h = F(g), F(h) # Convert inputs to field elements

    phi = p - 1 # Eulers totient function for prime p
    factors = factor(phi) # Prime factorization of phi

    q_max = max(p for p, _ in factors) # Largest prime factor of p - 1
    B = 50 # Bound on maximum bit length for q_max
    
    if q_max >= 2 ** B: # Check q is within bound B
        print(f'Input Error: Largest factor of p-1 larger than 2^{B}')
        return None

    remainders = [] # Remainders for Chinese Remainder Theorem
    moduli = [] # Moduli for Chinese Remainder Theorem

    # Solves for x (mod q^e)
    for q, e in factors:
        x = 0 # x = x_0 + x_1 * q + ... + x_e-1 * q^e-1 
        h_current = h # Value of h adjusted for each x_i
        rhs = g ** (phi // q) # rhs constant for each x_i

        # Iterates through i -> [0, e) to find all x_i
        for i in range(e):
            lhs = h_current ** (phi // (q ** (i + 1))) # lhs adjusted for each x_i
            x_i = None

            # Solves lhs = rhs^x_i (mod p) for x_i -> [0, q)   
            if q > 100:
                # If q large we use pollard rho in subgroup of order q
                x_i = pollard_rho(p, rhs, lhs, q)
            else:
                # If q small we brute force efficiently
                rhs_j = F(1) # Start with rhs^0 (j = 0)
                for j in range(q):
                    if lhs == rhs_j:
                        x_i = j
                        break
                    rhs_j *= rhs # Multiply by rhs each time to avoid exponentiation

            # If no x_i is found return error
            if x_i == None:
                print('Error: No Solution')
                return None

            x += (q ** i) * x_i # Adds new term to partial solution
            h_current *= g ** (-x_i * (q ** i)) # Updates h for next term

        # Saves x (mod q^e)
        remainders.append(x)
        moduli.append(q ** e)
        
    # Solves linear congruence x (mod q_1^e_1) ... x (mod q_n^e_n) = x (mod p - 1)
    return crt(remainders, moduli)