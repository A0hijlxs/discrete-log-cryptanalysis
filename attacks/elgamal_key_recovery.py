from sage.all import ceil, randint, gcd, xgcd, GF, ZZ, log

p = 110214139244619628817214220180759903623772273476973237581357926442068242777290742678308432173600447807045877802350820689329189906705525673103048044191741443155435676500083806328416857042655377621165517621594416756188456115632843630925048767223256580171880844584730175829519130860391756849271479689433096739183

F = GF(p)
g = F.multiplicative_generator()

pk = 34433677938790370326841544538327162949912651400435132418106303077870457237143764454742015325166343918042990360062245221128902045768722718013478894065082541995839757102391295145783918223456244521021455917802117759229766342977568038582505027961704596375794083965753629611033532591555874758736196549877539223439

def oracle(m):
    # this secret key is supposed to be SECRET!!!
    # this oracle is supposed to be a black box for you
    sk = 75634685477382510444330864520879772958994529678796910222627902736886490142385035840900624825784171137820168937351129077803696658896294516185852549440076452376282425274587541505371219507459795594844038021894626666390469834141313268358007359600087991446362848017047148793330467454171907456319139352116641008518

    log_p = ceil(log(p, 2))
    k = randint(0, log_p)
    while gcd(k, p-1) > 1:
        k = randint(0, log_p)

    one, k_inv, _ = xgcd(k, p-1)
    assert one == 1

    r = g ** k

    sig = ( k_inv * (m - sk  * ZZ(r)) ) % (p - 1)
    return r, sig


def find_collision():
    """
    Finds a collision in signature space based on the oracle function.
    A collision occurs when two different messages produce the same r value in their signatures. 
    Returns:
        tuple: (r, (sig_1, message_1), (sig_2, message_2)) if a collision is found.
        None: If no collision is found within p attempts.
    """
    signatures = dict() # Dictionary to store obtained r: (s, m) values
    for _ in range(p): # Collision expected after sqrt(size of signature space) iterations
        message = ZZ.random_element(p)
        r, sig = oracle(message) # Query oracle for signature

        if r in signatures: # Check if collision found
            return r, (sig, message), signatures[r] # Return collision
        
        signatures[r] = (sig, message) # Save new signature
    return None


def key_recovery_attack():
    """
    Performs the attack to compute the private key by finding a collision in signatures,
    then solving for k and sk using modular arithmetic.
    Returns:
        sk (int): The private key if the attack is successful.
        None: If no collision is found or if required values are not invertible.
    """
    collision = find_collision()
    # Check a collision was found
    if not collision:
        print('Error: No Collision Found')
        return None
    
    r, (sig_1, message_1), (sig_2, message_2) = collision # Unpack collision values

    # (s_2 - s_1)k = (m_2 - m_1) (mod p - 1)
    delta_s = sig_2 - sig_1 # Lhs
    delta_m = message_2 - message_1 # Rhs

    # Check and compute lhs^-1
    one, delta_s_inv, _ = xgcd(delta_s, p - 1)
    if one != 1:
        print('Error: delta_s Not Invertible')
        return None
    
    k = (delta_m * delta_s_inv) % (p - 1) # Solve for k
    
    # Check and compute r^-1
    one, r_inv, _ = xgcd(ZZ(r), p - 1)
    if one != 1:
        print('Error: r Not Invertible')
        return None
    
    # (r * sk) = m - (sig * k) (mod p - 1)
    sk = ((message_1 - (sig_1 * k)) * r_inv) % (p - 1) # Solve for sk
    return sk

def main():
    print(key_recovery_attack())

if __name__ == '__main__':
    main()