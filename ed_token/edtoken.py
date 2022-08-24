from typing import List, Optional, Union

from ed_token.token_cipher import AsymTokenCipher, SymTokenCipher
from ed_token.utils.exceptions import ProfileNotFound
from ed_token.utils.json_files import JsonFiles
from ed_token.utils.models import Cipher, Profile
from ed_token.utils.templates import CommandTemplate


class EDToken:
    def __init__(self, profile: Optional[str] = None, path: str = ""):
        self.profile_id: Optional[str] = profile
        self.path: str = path
        self.profile: Optional[Profile] = None
        if self.profile_id:
            self.load_profile(self.profile_id)

    def remove_profile(self, profile_id: str, path: Optional[str] = None) -> None:
        path = path if path else self.path
        with JsonFiles(path) as user_json_obj:
            user_json_obj.remove_key(profile_id)

        if profile_id == self.profile_id:
            self.profile_id, self.profile = None, None

    def remove_profile_content(self, key: str) -> None:
        if self.profile is None:
            raise RuntimeError("No profile has been initializate")

        with JsonFiles(self.path) as user_json_obj:
            user_json_obj.remove_key([self.profile_id, key])
            self.profile.content = user_json_obj.content

    def save_profile(self, path=None) -> None:
        with JsonFiles(self.path) as user_json_obj:
            user_json_obj.set_value(self.profile_id, self.profile.content)

    def load_profile(self, profile_id: str) -> Optional[Profile]:
        profile: Optional[Dict]
        with JsonFiles(self.path) as user_json_obj:
            profile = user_json_obj.get_value(profile_id)

        if profile == None:
            self.profile_id, self.profile = None, None
            return None
        else:
            self.profile_id = profile_id
            self.profile = Profile(**{"id": profile_id, "content": profile})
            return self.profile

    def initialize_profile(self, profile_name: str) -> Profile:
        self.profile_id = profile_name
        self.profile = Profile(**{"id": profile_name, "content": {}})
        return self.profile

    def get_all_profiles(self) -> List[str]:
        with JsonFiles(self.path) as user_json_obj:
            return user_json_obj.list_keys()

    def set_template(self, template: str) -> None:
        self.set_content_to_profile("template", template)

    def set_content_to_profile(
        self, token_id: str, token: str, cipher: Optional[Cipher] = None,
    ) -> None:
        if cipher and cipher.type == "sym":
            tchiper = SymTokenCipher(token, token_id)
            token = tchiper.encrypt(cipher.key)
        elif cipher and cipher.type == "asym":
            raise NotImplementedError()

        self.profile.set_token(token_id, token)
