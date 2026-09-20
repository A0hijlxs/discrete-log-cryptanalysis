from sage.all import GF

from dlp.pohlig_hellman import pohlig_hellman
from dlp.bsgs import BSGS
from dlp.pollard_rho import pollard_rho
from dlp.enhanced_pohlig_hellman import enhanced_pohlig_hellman
from dlp.index_calculus import IC

from tests.helpers import retry

# p - 1 = 3820 = 2^2 * 5 * 191, smooth enough for pohlig_hellman/enhanced/IC.
# 191 is prime, used directly as a prime-order subgroup for BSGS/pollard_rho.
P = 3821
Q = 191


def _full_group_instance(x):
    F = GF(P)
    g = F.multiplicative_generator()
    return int(g), int(g ** x)


def _prime_subgroup_instance(x):
    F = GF(P)
    g = F.multiplicative_generator()
    gq = g ** ((P - 1) // Q)
    return int(gq), int(gq ** x)


def test_pohlig_hellman():
    g, h = _full_group_instance(1234)
    assert pohlig_hellman(P, g, h) == 1234


def test_enhanced_pohlig_hellman():
    g, h = _full_group_instance(1234)
    assert enhanced_pohlig_hellman(P, g, h) == 1234


def test_index_calculus():
    g, h = _full_group_instance(1234)
    assert retry(IC, P, g, h) == 1234


def test_bsgs():
    g, h = _prime_subgroup_instance(57)
    assert BSGS(P, g, h, Q) == 57


def test_pollard_rho():
    g, h = _prime_subgroup_instance(57)
    assert pollard_rho(P, g, h, Q) == 57
