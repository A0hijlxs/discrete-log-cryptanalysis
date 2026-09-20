from crypto.elgamal import (
    generate_safe_prime,
    generate_public_parameters,
    elgamal_keygen,
    elgamal_sign,
    elgamal_verify,
)
from crypto.finite_fields_demo import generate_DH_keys, compute_shared_secret
from crypto.ctr_xor_recovery import plaintext_ascii


def test_elgamal_sign_and_verify_roundtrip():
    p, q = generate_safe_prime(64)
    g = generate_public_parameters(p, q, True)
    m = 42

    sk, pk = elgamal_keygen(p, g)
    signature = elgamal_sign(p, g, m, sk)
    assert elgamal_verify(p, g, m, pk, signature)

    _, other_pk = elgamal_keygen(p, g)
    assert not elgamal_verify(p, g, m, other_pk, signature)


def test_finite_fields_diffie_hellman_shared_secret():
    sk_a, pk_a = generate_DH_keys()
    sk_b, pk_b = generate_DH_keys()
    assert compute_shared_secret(sk_a, pk_b) == compute_shared_secret(sk_b, pk_a)


def test_ctr_xor_recovery_plaintext():
    assert plaintext_ascii == "Francois wears odd socks.\n"
