#!/usr/bin/env python3

import argparse
import getpass
from subprocess import PIPE, Popen
from sys import path, stdin
from typing import Any

from ed_token.token_cipher import AsymTokenCipher, SymTokenCipher
from ed_token.utils import paths
from ed_token.utils.json_files import JsonFiles
from ed_token.utils.templates import CommandTemplate
from ed_token.wallet import Wallet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="EDToken commands", formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "main",
        choices=["add", "set", "remove", "show", "exec", "wallet", "closewallet"],
        help="""
            EDToken
            Execute an action:

            add          Add a EDToken profile
            set          Set profile values using key and encryptation algorithms
            remove       Removes a profile or keys in the profile
            show         Show the profile data or show all profiles with ""
            exec         Executes command template
            wallet       Decrypt a file set in the profile with the key "file"
            closewallet  Encrypt the decrypted file 
        """,
    )
    parser.add_argument("profilename", help="Positional argument to select a profile")

    parser.add_argument("-k", "--key", help="Set a id to get profile value")
    parser.add_argument("-v", "--value", help="Set a profile value")
    parser.add_argument(
        "-i", "--input", help="Set a value for the dictionary using a file or pipe",
    )
    parser.add_argument(
        "--sym", action="store_true", help="Symetric key to encrypt or decrypt value"
    )
    parser.add_argument(
        "--asym",
        action="store_true",
        help="Uses asymetric encryptation to encrypt value",
    )
    parser.add_argument("--temp", nargs=1, help="Set a command template")
    parser.add_argument("-rp", "--rmprofile", nargs=1, help="Remove a profile")
    parser.add_argument(
        "-rfp", "--rmfromprofile", nargs=1, help="Remove a key in the profile"
    )

    parser.add_argument(
        "-vv", "--verbose", action="store_true", help="Show the profile values after the applied changes"
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


def exists_crypted_values(profile_name: str) -> bool:
    with JsonFiles(paths.user_json()) as user_json_obj:
        profile_content = user_json_obj.get_value(profile_name)
        return profile_content["crypted-values"]


def command_set(args: argparse.Namespace):
    profile_name = args.profilename
    k, v = args.key, args.value
    crypted_values = False

    if args.sym:
        crypted_values = True
        tchiper = SymTokenCipher(_show_input_hiding("Enter a token: "), k)
        encryptation_key = _show_input_hiding("Enter a password: ")
        v = tchiper.encrypt(encryptation_key)
    elif args.asym:
        raise NotImplementedError()
    elif args.temp is not None:
        k = "template"
        if args.input is not None:
            _get_input(args.input)
        else:
            v = args.temp[0]

    with JsonFiles(paths.user_json()) as user_json_obj:
        user_json_obj.set_value(profile_name, {k: v})
        user_json_obj.set_value(profile_name, {"crypted-values": crypted_values})


def command_add(args: argparse.Namespace):
    profile_name = args.profilename
    with JsonFiles(paths.user_json()) as user_json_obj:
        user_json_obj.set_value(profile_name, {})


def command_remove(args: argparse.Namespace):
    profile_name = args.profilename
    key = args.key
    with JsonFiles(paths.user_json()) as user_json_obj:
        if key is None:
            user_json_obj.remove_key(profile_name)
        else:
            user_json_obj.remove_key([profile_name, key])


def list_all_profiles():
    with JsonFiles(paths.user_json()) as user_json_obj:
        profiles = user_json_obj.list_keys()
        for i, profile in enumerate(profiles):
            print("%s. %s" % (i + 1, profile))


def command_show(args: argparse.Namespace):
    profile = args.profilename
    if profile == "":
        list_all_profiles()
    else:
        with JsonFiles(paths.user_json()) as user_json_obj:
            profile_content = user_json_obj.get_value(args.profilename)
            print(JsonFiles.pretty_print(profile_content))


def command_exec(args: argparse.Namespace):
    profile_name = args.profilename
    cipher_type, key_cert = None, None
    if args.sym is not None:
        cipher_type = "sym"
        key_cert = _show_input_hiding("Enter a password: ")
    elif args.asym is not None:
        raise NotImplementedError()
    elif exists_crypted_values(profile_name):
        raise Exception("Pls select a cipher type.")

    with JsonFiles(paths.user_json()) as user_json_obj:
        command = (CommandTemplate(profile_name, cipher_type, key_cert)).get_command()
        print(f"Command executed: {command}")
        proc = Popen(command, shell=True)


def command_wallet(args: argparse.Namespace):
    profile_name: str = args.profilename
    file_path: str = ""

    with JsonFiles(paths.user_json()) as user_json_obj:
        content: Dict = user_json_obj.get_value(profile_name)
        file_path = content["file"]

    wallet: Wallet = Wallet(file_path, paths.user_json(), profile_name)
    key: str = _show_input_hiding("Key to decrypt file: ")
    wallet.open_file(key)


def command_closewallet(args: argparse.Namespace):
    profile_name: str = args.profilename
    file_path: str = ""

    with JsonFiles(paths.user_json()) as user_json_obj:
        content: Dict = user_json_obj.get_value(profile_name)
        file_path = content["file"]

    wallet: Wallet = Wallet(file_path, paths.user_json(), profile_name)
    wallet.close_file()


command_map = {
    "add": command_add,
    "set": command_set,
    "remove": command_remove,
    "show": command_show,
    "exec": command_exec,
    "wallet": command_wallet,
    "closewallet": command_closewallet,
}


def main():
    args = parse_args()
    command_map[args.main](args)
    if args.verbose: command_show(args) 


if __name__ == "__main__":
    main()
