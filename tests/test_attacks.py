from attacks.elgamal_key_recovery import p, g, pk, key_recovery_attack
from attacks.hastad_broadcast import main as hastad_main

from tests.helpers import retry

# Known-good result of the fixed CRT + integer cube root computation in
# hastad_broadcast.main() against its hardcoded N1/N2/N3/C1/C2/C3.
EXPECTED_HASTAD_MESSAGE = "125213347708887948115126001467664467596282356031075701717302323192402682548209853517398481012036934041292536476067163341428270196339024382330146213915725132875663753461936722927533341901433197782705149151335189031955425571430823937555135624597233750204058456400923399067789266312145658948130059887520815157"


def test_elgamal_key_recovery():
    sk = retry(key_recovery_attack, attempts=20)
    assert sk is not None
    assert pow(int(g), sk, p) == pk


def test_hastad_broadcast(capsys):
    hastad_main()
    captured = capsys.readouterr()
    assert captured.out.strip() == EXPECTED_HASTAD_MESSAGE
