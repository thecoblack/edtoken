import os
import shutil

from typing import List

from ed_token.utils import paths
from ed_token.edtoken import EDToken
from ed_token.utils.templates import CommandTemplate


class Wallet:
    def __init__(self, file_path: str, profiles_file_path: str, profile_id: str):
        self.file_path: str = file_path 
        self.cache_path: str = f"{paths.cache()}/{os.path.basename(file_path)}"
        self.edtoken: EDToken = EDToken(path=profiles_file_path)

        if not self.edtoken.load_profile(profile_id):
            self.edtoken.initialize_profile(profile_id)

        if os.path.exists(self.file_path):
            self.cred_file = open(self.file_path, "r")
        else: raise FileNotFoundError("File not found")


    def decrypt_file(self, decrypt_key: str) -> List[str]:
        template = CommandTemplate(
            cipher_type="sym",
            decrypt_key=decrypt_key,
            content=self.edtoken.profile.content
        )
        decripted_file: List[str] = []
        for line in self.cred_file:
            template.template = line
            decripted_file.append(template.get_command())

        return decripted_file

    def open_file(self, decrypt_key: str) -> None:
        decripted_lines: List[str] = self.decrypt_file(decrypt_key)
        self.move_to_cache()
        with open(self.file_path, "w") as f:
            for line in decripted_lines:
                f.write(line)

    def close_file(self) -> None:
        self.restore_file_from_cache()

    def move_to_cache(self) -> None:
        shutil.copy(self.file_path, self.cache_path)

    def restore_file_from_cache(self) -> None:
        os.remove(self.file_path)
        shutil.copy(self.cache_path, self.file_path)
        os.remove(self.cache_path)
