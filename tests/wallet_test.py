import os
import json
import pytest

from ed_token.edtoken import EDToken
from ed_token.wallet import Wallet
from ed_token.utils import paths
from ed_token.utils.models import Cipher


def test_init_wallet(tmp_path):
    json_path = f"{tmp_path}/user_data.json"
    with open(json_path, "w") as user_data:
        user_data.write(json.dumps({}, indent=4))

    path: str = f"{tmp_path}/encrypted_file"
    with open(path, "w") as encrypted_file: pass

    edtoken = EDToken("test-profile", json_path)
    with pytest.raises(RuntimeError):
        wallet = Wallet(path, edtoken) 

    wrong_path: str = f"/wrong_path/encrypted_file"
    edtoken.initialize_profile("test-profile")
    with pytest.raises(FileNotFoundError):
        wallet = Wallet(wrong_path, edtoken) 


@pytest.fixture
def wallet(tmp_path):
    json_path = f"{tmp_path}/user_data.json"
    with open(json_path, "w") as user_data:
        user_data.write(json.dumps({}, indent=4))

    path: str = f"{tmp_path}/encrypted_file"
    with open(path, "w") as encrypted_file:
        encrypted_file.write("user={user}\npass={?token}")

    edtoken: EDToken = EDToken(path=json_path)
    edtoken.initialize_profile("test-profile")
    edtoken.set_content_to_profile("user", "test-profile")
    edtoken.set_content_to_profile(
        "token",
        "token_01",
        Cipher(**{
            "type": "sym",
            "key": "test"
        })
    )
    wallet = Wallet(path, edtoken)
    return wallet

def test_decrypt_file(tmp_path, wallet):
    decrypted_file = wallet.decrypt_file("test")
    assert decrypted_file == ["user=test-profile\n", "pass=token_01"]


def test_open_close_file(tmp_path, wallet):
    decrypted_lines = ["user=test-profile\n", "pass=token_01"]
    encrypted_lines = ["user={user}\n", "pass={?token}"]
    cache_path = f"{paths.cache()}/encrypted_file"

    wallet.open_file("test")
    with open(wallet.file_path, 'r') as decrypted_file:
        for i, line in enumerate(decrypted_file):
            assert decrypted_lines[i] == line

    assert os.path.exists(cache_path)
    with open(cache_path, 'r') as cache_file:
        for i, line in enumerate(cache_file):
            assert encrypted_lines[i] == line

    wallet.close_file()
    assert os.path.exists(wallet.file_path)
    with open(wallet.file_path, 'r') as encrypted_file:
        for i, line in enumerate(encrypted_file):
            assert encrypted_lines[i] == line
    assert not os.path.exists(cache_path)


def test_open_close_file_already_exists(wallet):
    wallet.open_file("test")
    with pytest.raises(RuntimeError): 
        wallet.open_file("test")

    wallet.close_file()
    with pytest.raises(RuntimeError): 
        wallet.close_file()
