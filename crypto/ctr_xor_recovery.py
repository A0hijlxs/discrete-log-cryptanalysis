"""CTR/XOR keystream-reuse plaintext recovery ("Fashion Icon").

`ctr` (crypto/data/ctr) is a black-box CTR-mode oracle with a fixed,
unknown key: given a nonce and an input, it XORs the input with
keystream(key, nonce). Reusing the same nonce to "encrypt" an all-zero
input exposes the raw keystream directly, since 0 XOR keystream =
keystream -- XOR's self-inverse property under a reused nonce/key. That
keystream can then decrypt any other ciphertext captured under the same
nonce, such as fashion_hex below.

Reproduce with the included oracle (crypto/data/ctr) and crypto/data/*.hex
from the repo root; the two invocations are shown as comments next to
keystream_hex and message_hex below.
"""

fashion_hex = 'ed6d300532eba03c1e5d3a2a73f90bafa9e92a05e7485f57aec2'
nonce_hex = '59554d4d594255525249544f464c414e'

zeros_hex = '0000000000000000000000000000000000000000000000000000'

# echo -n "$zeros_hex" > zeros.hex; ctr $(cat crypto/data/nonce.hex) $(cat zeros.hex) > keystream.hex
keystream_hex = 'ab1f516b5184c94f3e2a5f4b018a2bc0cd8d0a76882b342480c8'

# ctr $(cat crypto/data/nonce.hex) $(cat crypto/data/fashion.hex) > message.hex
message_hex = '4672616e636f6973207765617273206f646420736f636b732e0a'

plaintext_ascii = bytes.fromhex(message_hex).decode('ascii')
