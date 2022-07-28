import re
from base64 import b64decode
from pathlib import Path

from ed_token.token_cipher import AsymTokenCipher, SymTokenCipher
from ed_token.utils import paths
from ed_token.utils.json_files import JsonFiles


class CommandTemplate:
    def __init__(self, name="", cipher_type=None, decrypt_key=None, content=None):
        self.name = name
        self.decrypt_key = decrypt_key
        self.cipher_type = cipher_type
        self.json_file_obj = JsonFiles(paths.user_json())

        if not content:
            self.content = self.json_file_obj.get_value(name)
        else:
            self.content = content
        self.template = self.content["template"] if "template" in self.content else ""

    def _get_blocks(self) -> list:
        return re.findall(r"\{(\?{0}[\w-]+)\}", self.template)

    def _get_crypted_blocks(self) -> list:
        return re.findall(r"\{(\?{1}[\w-]+)\}", self.template)

    def _set_blocks_values(self, command: str, dict_values: dict) -> str:
        for value in dict_values.values():
            command = re.sub(r"\{(\?{0}[\w-]+)\}", value, command, 1)
        return command

    def _set_crypted_blocks_values(
        self, command: str, crypted_dict_values: dict
    ) -> str:
        if self.cipher_type == "sym":
            for key, value in crypted_dict_values.items():
                if not type(value) == dict:
                    continue
                encrypted_token = b64decode(value["token"].encode("utf-8"))
                iv = b64decode(value["cbc_iv"].encode("utf-8"))
                padding = value["padding_size"]
                tcipher = SymTokenCipher(encrypted_token, padding)
                decrypted_token = tcipher.decrypt(self.decrypt_key, iv)
                command = re.sub(r"\{(\?{1}[\w-]+)\}", decrypted_token, command, 1)
        elif self.cipher_type == "asym":
            raise NotImplementedError()
        return command

    def get_command(self) -> str:
        dict_values = {}
        crypted_dict_values = {}
        keys = self._get_blocks()
        crypted_keys = self._get_crypted_blocks()
        try:
            for key in keys:
                dict_values[key] = self.content[key]
            for crypted_key in crypted_keys:
                crypted_dict_values[crypted_key[1:]] = self.content[crypted_key[1:]]
        except KeyError as err:
            print(err)

        command = self._set_blocks_values(self.template, dict_values)
        command = self._set_crypted_blocks_values(command, crypted_dict_values)
        return command
