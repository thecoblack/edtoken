import json
from typing import Dict, Optional, Union

from pydantic import BaseModel

from utils.templates import CommandTemplate


class Cipher(BaseModel):
    type: str
    key: str


class Profile(BaseModel):
    id: str
    template: str = ""
    content: Optional[Dict] = None

    def __str__(self) -> str:
        return json.dumps({self.id: self.content}, indent=4)

    def set_token(self, id: str, token: str) -> None:
        self.content[id] = token

    def get_token(self, id: str) -> Union[str, int, None]:
        return self.content[id] if id in self.content else None

    def get_dict(self) -> Dict:
        return {self.id: self.content}

    def get_template(self, cipher_type: Optional[str], key: str = "") -> str:
        if cipher_type == "sym" or not cipher_type:
            return CommandTemplate(self.id, "sym", key, self.content).get_command()
        elif cipher_type == "asym":
            raise NotImplementedError()
