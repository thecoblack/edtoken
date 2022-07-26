from ed_token.token_cipher import SymTokenCipher
from ed_token.utils.templates import CommandTemplate


def test_get_complete_command_by_content():
    tchiper = SymTokenCipher("test-token")
    encripted_token = tchiper.encrypt("test")

    ct = CommandTemplate(
        cipher_type="sym",
        decrypt_key="test",
        content={
            "user": "test_user",
            "token": encripted_token,
            "template": "{?token} {user}",
        },
    )

    assert ct.get_command() == "test-token test_user"
