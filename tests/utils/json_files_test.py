import json

import pytest

from ed_token.utils.json_files import JsonFiles


@pytest.fixture
def json_file(tmp_path):
    path = f"{tmp_path}/user_data.json"
    with open(path, "w") as test_file:
        test_file.write(
            json.dumps(
                {
                    "test-profile": {
                        "token1": "asdfasdfasdf",
                        "token2": {},
                        "template": "{token1} {token2}",
                    }
                },
                indent=4,
            )
        )
    return JsonFiles(path)


def test_list_keys(json_file):
    keys = json_file.list_keys()
    assert keys == ["test-profile"]
    keys = json_file.list_keys("test-profile")
    assert keys == ["token1", "token2", "template"]


def test_set_get_value(json_file):
    profile = json_file.get_value("test-profile")
    assert profile == {
        "token1": "asdfasdfasdf",
        "token2": {},
        "template": "{token1} {token2}",
    }

    json_file.set_value("new-profile", {"token": ""})
    profile = json_file.get_value("new-profile")
    assert profile == {"token": ""}


def test_remove_key(json_file):
    json_file.remove_key(["test-profile", "token1"])
    profile = json_file.get_value("test-profile")
    assert profile == {"token2": {}, "template": "{token1} {token2}"}

    json_file.remove_key("test-profile")
    assert json_file.get_value("test-profile") == None


def test_with_statement(tmp_path):
    path = f"{tmp_path}/user_data.json"
    with open(path, "w") as user_data_file:
        user_data_file.write(json.dumps({}, indent=4))

    with JsonFiles(path) as json_file:
        json_file.set_value("test-profile", {})

    jf = JsonFiles(path)
    assert jf.get_value("test-profile") == {}
