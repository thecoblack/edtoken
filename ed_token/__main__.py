#!/usr/bin/env python3
import argparse
import getpass
from subprocess import PIPE, Popen
from sys import path, stderr, stdin, stdout
from typing import Any, Callable, Dict, Optional, Union

from ed_token.edtoken import EDToken
from ed_token.utils import paths
from ed_token.utils.json_files import JsonFiles
from ed_token.utils.models import Cipher
from ed_token.wallet import Wallet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="EDToken commands", formatter_class=argparse.RawTextHelpFormatter
    )
    subparser = parser.add_subparsers(help="")

    wallet_parser = subparser.add_parser("wallet", help="Actions for using the wallet")
    wallet_parser.formatter_class = argparse.RawTextHelpFormatter
    wallet_group = wallet_parser.add_argument_group("Wallet")
    wallet_group.add_argument(
        "wallet_action",
        choices=["open", "close"],
        help=(
            "\nopen   Decrypts file contents\n" "close  Re-encrypt file contents\n\n"
        ),
    )
    wallet_group.add_argument(
        "profilename", help="Profile name to obtain the saved configurations"
    )

    list_parser = subparser.add_parser("list", help="Show all saved profiles")
    list_group = list_parser.add_argument_group("List")
    list_group.add_argument("list", action="store_true", help="")

    profile_actions_parser = subparser.add_parser(
        "profile", help="Actions to interact with the profiles"
    )
    profile_actions_parser.formatter_class = argparse.RawTextHelpFormatter
    profile_actions_group = profile_actions_parser.add_argument_group("Profile actions")

    profile_actions_group.add_argument(
        "profile_action",
        choices=["add", "set", "get", "remove", "show", "exec"],
        help=(
            "\nadd          Add a EDToken profile\n"
            "set          Set profile values using key and encryptation algorithms\n"
            "get          Get a profile value\n"
            "remove       Removes a profile or keys in the profile\n"
            "show         Show the profile data\n"
            "exec         Executes command template\n\n"
        ),
    )
    profile_actions_group.add_argument(
        "profilename", help="Profile name to obtain the saved configurations"
    )

    profile_actions_group.add_argument(
        "-k", "--key", help="Set a id to get profile value"
    )
    profile_actions_group.add_argument("-v", "--value", help="Set a profile value")
    profile_actions_group.add_argument(
        "-i", "--input", help="Set a value for the dictionary using a file or pipe",
    )
    profile_actions_group.add_argument(
        "--sym", action="store_true", help="Symetric key to encrypt or decrypt value"
    )
    profile_actions_group.add_argument(
        "--asym",
        action="store_true",
        help="Uses asymetric encryptation to encrypt value",
    )
    profile_actions_group.add_argument("--temp", help="Set a command template")
    profile_actions_group.add_argument(
        "--file", help="Set the file path in the profile"
    )
    profile_actions_group.add_argument(
        "-rfp", "--rmfromprofile", help="Remove a key in the profile"
    )
    profile_actions_group.add_argument(
        "-vv",
        "--verbose",
        action="store_true",
        help="Show the profile values after the applied changes",
    )

    args = parser.parse_args()
    return args


def _show_input_hiding(msg: str) -> str:
    return getpass.getpass(msg)


def _get_input(args_value: str) -> Any:
    if not stdin.isatty():
        return stdin.read()
    else:
        with open("args_value", "r") as f:
            return f.read()


def exists_crypted_values(edtoken: EDToken) -> bool:
    return edtoken.profile.get_token("crypted-values") > 0


def command_set(args: argparse.Namespace, edtoken: EDToken):
    k: str = args.key
    v: str = args.value
    crypted_values: int = edtoken.profile.get_token("crypted-values")
    crypted_values += int(any([args.sym, args.asym]))

    if args.sym:
        token: str = _show_input_hiding("Enter a token: ")
        cipher_key: str = _show_input_hiding("Enter a password: ")
        edtoken.set_content_to_profile(
            k, token, Cipher(**{"type": "sym", "key": cipher_key})
        )
    elif args.asym:
        raise NotImplementedError()
    elif args.temp is not None:
        edtoken.set_template(args.temp)
    elif args.file is not None:
        edtoken.set_content_to_profile("file", args.file)
    elif k is not None and v is not None:
        edtoken.set_content_to_profile(k, v)

    edtoken.set_content_to_profile("crypted-values", crypted_values)
    edtoken.save_profile()


def command_add(args: argparse.Namespace, edtoken: EDToken) -> None:
    if edtoken.profile is None:
        edtoken.initialize_profile(args.profilename)
        edtoken.set_content_to_profile("crypted-values", 0)
        edtoken.save_profile()
    else:
        print(f"The profile {args.profilename} already exists")


def command_remove(args: argparse.Namespace, edtoken: EDToken) -> None:
    key: str = args.rmfromprofile
    if key is None:
        response: str = ""
        while not response in ["n", "y"]:
            response = input("Are you sure? (y/n): ")
        if response == "y":
            edtoken.remove_profile(edtoken.profile_id)
    else:
        edtoken.remove_profile_content(key)


def list_all_profiles(edtoken: EDToken) -> None:
    profiles: List[str] = edtoken.get_all_profiles()
    for i, profile in enumerate(profiles):
        print("%s. %s" % (i + 1, profile))


def command_show(args: argparse.Namespace, edtoken: EDToken) -> None:
    if edtoken.profile is not None:
        profile_content: Dict = edtoken.profile.get_dict()
        print(JsonFiles.pretty_print(profile_content))
    else:
        print(f"The profile '{args.profilename}' does not exists")


def command_exec(args: argparse.Namespace, edtoken: EDToken) -> None:
    cipher_type: Optional[str] = None
    key_cert: Optional[str] = None

    if args.sym is not None:
        cipher_type = "sym"
        key_cert = _show_input_hiding("Enter a password: ")
    elif args.asym is not None:
        raise NotImplementedError()
    elif exists_crypted_values(edtoken):
        raise RuntimeError("Template includes an encrypted token, pls select a cipher.")

    command: str = edtoken.profile.get_template(cipher_type=cipher_type, key=key_cert)
    print(f"Command executed: {command}")
    proc = Popen(command, shell=True)


def command_get(args: argparse.Namespace, edtoken: EDToken) -> None:
    key: str = args.key
    value: Union[str, int, None] = edtoken.profile.get_token(key)

    if value is not None:
        print(value, file=stdout)
    else:
        print(None, file=stderr)


def command_wallet(edtoken: EDToken) -> None:
    file_path: Optional[str] = edtoken.profile.get_token("file")

    if file_path is None:
        RuntimeError(f"There is not set a file path in {edtoken.profile_id}")

    wallet: Wallet = Wallet(file_path, edtoken)
    key: str = _show_input_hiding("Key to decrypt file: ")
    wallet.open_file(key)


def command_closewallet(edtoken: EDToken) -> None:
    file_path: Optional[str] = edtoken.profile.get_token("file")

    if file_path is None:
        RuntimeError(f"There is not set a file path in {edtoken.profile_id}")

    wallet: Wallet = Wallet(file_path, edtoken)
    wallet.close_file()


def main():
    profile_actions: Dict[
        str, Callable[[argparse.argparse.Namespace, EDToken], None]
    ] = {
        "add": command_add,
        "set": command_set,
        "get": command_get,
        "remove": command_remove,
        "show": command_show,
        "exec": command_exec,
        "get": command_get,
    }

    wallet_actions: Dict[str, Callable[[EDToken], None]] = {
        "open": command_wallet,
        "close": command_closewallet,
    }

    args: argparse.Namespace = parse_args()
    if "profile_action" in args:
        edtoken: EDToken = EDToken(args.profilename, paths.user_json())
        profile_actions[args.profile_action](args, edtoken)
        if args.verbose:
            command_show(args, edtoken)
    elif "wallet_action" in args:
        edtoken: EDToken = EDToken(args.profilename, paths.user_json())
        wallet_actions[args.wallet_action](edtoken)
    elif "list" in args:
        edtoken: EDToken = EDToken(path=paths.user_json())
        list_all_profiles(edtoken)


if __name__ == "__main__":
    main()
