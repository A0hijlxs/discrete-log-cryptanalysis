
fashion_hex = 'ed6d300532eba03c1e5d3a2a73f90bafa9e92a05e7485f57aec2'
nonce_hex = '59554d4d594255525249544f464c414e'

zeros_hex = '0000000000000000000000000000000000000000000000000000'


# ctr $(cat nonce.hex) $(cat zeros.hex) > keystream.hex
keystream_hex = 'ab1f516b5184c94f3e2a5f4b018a2bc0cd8d0a76882b342480c8'

# ctr $(cat nonce.hex) $(cat fashion.hex) > message.hex
message_hex = '4672616e636f6973207765617273206f646420736f636b732e0a'


plaintext_ascii = bytes.fromhex(message_hex).decode('ascii')
print(plaintext_ascii)
