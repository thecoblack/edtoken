import json
from typing import Any, Optional, Union


class JsonFiles:
    def __init__(self, path: str):
        self.file = open(path, "r")
        self.path = path
        self.content = json.loads(self.file.read())
        self.modified_file = False

    def __enter__(self) -> "JsonFiles":
        return self

    def __exit__(self, type, value, traceback):
        if self.modified_file:
            self.save_changes()
        self.close_file()

    def remove_key(self, key: Union[str, list]):
        self.modified_file = True
        if type(key) == str:
            del self.content[key]
        else:
            del self.content[key[0]][key[1]]

    def get_value(self, key: str) -> Optional[Any]:
        return self.content[key]

    def list_keys(self, key: str = None) -> list:
        if key is not None:
            content = self.content[key]
        else:
            content = self.content
        return list(content.keys())

    def set_value(self, key: str, value: Union[str, dict]):
        self.modified_file = True
        if type(value) == str or not len(value):
            self.content[key] = value
        else:
            value_key_dict = list(value.keys())[0]
            self.content[key][value_key_dict] = value[value_key_dict]

    def save_changes(self):
        self.file = open(self.path, "w")
        json.dump(self.content, self.file, indent=4)

    def close_file(self):
        self.file.close()

    @staticmethod
    def pretty_print(content: str) -> str:
        return json.dumps(content, indent=4)
