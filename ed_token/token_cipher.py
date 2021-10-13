import os
import hashlib
from base64 import b64decode, b64encode
from typing import Optional, Tuple, Union

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)

IV_BLOCK_SIZE = 16


class SymTokenCipher:
    def __init__(self, token: str, padding_size: int = 0):
        self.token = token
        self.padding_size = padding_size

    def _get_chiper(
        self, key: bytes, iv: Optional[bytes] = None
    ) -> Union[Cipher, Tuple[Cipher, bytes]]:
        if iv is not None:
            return Cipher(algorithms.AES(key), modes.CBC(iv))
        else:
            iv = os.urandom(IV_BLOCK_SIZE)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            return cipher, iv

    def _get_32_bytes_key(self, key: str) -> bytes:
        return hashlib.sha256(key.encode()).digest()[:32]

    def _set_token_padding(self, token, curr_length):
        self.padding_size = IV_BLOCK_SIZE - curr_length
        padded_token = token + os.urandom(self.padding_size)
        return padded_token

    def _get_token_blocks(self):
        token_blocks = []
        for i in range(0, len(self.token), IV_BLOCK_SIZE):
            if i + (IV_BLOCK_SIZE) > len(self.token):
                len_last_block = len(self.token) - i
                last_block = self.token[i : i + len_last_block]
                token_blocks.append(self._set_token_padding(last_block, len_last_block))
            else:
                token_blocks.append(self.token[i : i + 16])
        return token_blocks

    def encrypt(self, key: str) -> dict:
        self.token = self.token.encode("utf8")
        cipher, iv = self._get_chiper(self._get_32_bytes_key(key))
        encrypted_context = cipher.encryptor()

        self.token = self._get_token_blocks()
        blocks_context = b""
        for block in self.token:
            blocks_context += encrypted_context.update(block)

        encrypted_token = blocks_context + encrypted_context.finalize()
        return {
            "token": b64encode(encrypted_token).decode("utf-8"),
            "cbc_iv": b64encode(iv).decode("utf-8"),
            "padding_size": self.padding_size,
        }

    def decrypt(self, key: str, iv: bytes) -> str:
        cipher = self._get_chiper(self._get_32_bytes_key(key), iv)
        decrypted_ctx = cipher.decryptor()

        self.token = self._get_token_blocks()
        blocks_context = b""
        for block in self.token:
            blocks_context += decrypted_ctx.update(block)

        utf8_token = blocks_context + decrypted_ctx.finalize()
        return utf8_token[: -self.padding_size].decode("utf-8")


class AsymTokenCipher:
    def __init__(self, token):
        self.token = token

    def load_key(
        self,
        path: str,
        t: Union[rsa.RSAPublicKey, rsa.RSAPrivateKey] = rsa.RSAPrivateKey,
    ) -> Union[rsa.RSAPublicKey, rsa.RSAPrivateKey]:
        pass

    @staticmethod
    def get_private_key() -> rsa.RSAPrivateKey:
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)

    @staticmethod
    def get_public_key(private_key: rsa.RSAPrivateKey) -> rsa.RSAPublicKey:
        return private_key.public_key()

    @staticmethod
    def verify(public_key: rsa.RSAPublicKey, signature: bytes, token: bytes) -> bool:
        public_key.verify(
            signature,
            token,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(hashes.SHA256()),
        )

    @staticmethod
    def sign(private_key: rsa.RSAPrivateKey, token) -> bytes:
        signature = private_key.sign(
            token,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return signature

    def encrypt(self, public_key: rsa.RSAPublicKey) -> bytes:
        encrypted_token = public_key.encrypt(
            self.token,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return encrypted_token

    def decrypt(self, private_key: rsa.RSAPrivateKey, signature: bytes) -> str:
        decrypted_token = private_key.decrypt(
            self.token,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None
            ),
        )
        return decrypted_token
