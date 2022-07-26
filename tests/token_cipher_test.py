from base64 import b64decode

from ed_token.token_cipher import AsymTokenCipher, SymTokenCipher


def test_encrypt_decrypt():
    tcipher = SymTokenCipher("token")
    encrypted_token = tcipher.encrypt("token_key")

    tcipher = SymTokenCipher(
        b64decode(encrypted_token["token"].encode("utf-8")),
        encrypted_token["padding_size"],
    )
    decrypted_token = tcipher.decrypt(
        "token_key", b64decode(encrypted_token["cbc_iv"].encode("utf-8"))
    )
    assert decrypted_token == "token"
