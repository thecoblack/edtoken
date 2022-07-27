import json
import os

import pytest

from ed_token.edtoken import EDToken
from ed_token.utils.exceptions import ProfileNotFound
from ed_token.utils.models import Cipher, Profile


def test_initialize_profile():
    edt = EDToken()
    edt.initialize_profile("test-profile")
    assert edt.profile.content == {}


def test_save_profile(tmp_path):
    path = f"{tmp_path}/user_data.json"
    with open(path, "w") as user_data:
        user_data.write(json.dumps({}, indent=4))

    edt = EDToken(path=f"{tmp_path}/user_data.json")
    edt.initialize_profile("test-profile")
    edt.save_profile()

    saved_data = None
    with open(path, "r") as user_data:
        saved_data = json.load(user_data)
    assert {edt.profile_id: edt.profile.content} == saved_data


def test_load_profile(tmp_path):
    path = f"{tmp_path}/user_data.json"
    with open(path, "w") as user_data:
        user_data.write(json.dumps({"test-profile": {}}, indent=4))

    edt = EDToken(path=path)
    edt.load_profile("test-profile")
    assert {edt.profile_id: edt.profile.content} == {"test-profile": {}}

    edt.load_profile("nonexisting-profile")
    assert edt.profile == None


def test_get_all_profiles(tmp_path):
    path = f"{tmp_path}/user_data.json"
    with open(path, "w") as user_data:
        user_data.write(
            json.dumps(
                {"test-profile": {}, "test-profile2": {}, "test-profile3": {}}, indent=4
            )
        )

    edt = EDToken(path=path)
    profiles = edt.get_all_profiles()
    assert profiles == ["test-profile", "test-profile2", "test-profile3"]


def test_set_content_profile():
    edt = EDToken()
    edt.initialize_profile("test-profile")

    edt.set_content_to_profile("non_encrypted_token", "non_encrypted_token_01")
    assert not edt.profile.get_token("non_encrypted_token") == None

    edt.set_content_to_profile(
        "encrypted_token", "test_token_01", Cipher(**{"type": "sym", "key": "test"})
    )
    assert not edt.profile.get_token("encrypted_token") == None


def test_remove_profile(tmp_path):
    path = f"{tmp_path}/user_data.json"
    with open(path, "w") as user_data:
        user_data.write(json.dumps({"test-profile": {}}, indent=4))

    edt = EDToken(path=path)
    edt.remove_profile("test-profile")
    assert edt.get_all_profiles() == []
