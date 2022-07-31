#!/usr/bin/env python3

import argparse
import getpass
from subprocess import PIPE, Popen
from sys import path, stdin, stdout, stderr
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
    subparser = parser.add_subparsers(help="")

    wallet_parser = subparser.add_parser("wallet", help="Actions for using the wallet")
    wallet_parser.formatter_class = argparse.RawTextHelpFormatter
    wallet_group = wallet_parser.add_argument_group("Wallet")
    wallet_group.add_argument(
        "wallet_action",
        choices=["open", "close"],
        help=(
            "\nopen   Decrypts file contents\n"
            "close  Re-encrypt file contents\n\n"
        )
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
            v = args.temp
    elif args.file is not None:
        k, v = "file", args.file

    with JsonFiles(paths.user_json()) as user_json_obj:
        user_json_obj.set_value(profile_name, {k: v})
        user_json_obj.set_value(profile_name, {"crypted-values": crypted_values})


def command_add(args: argparse.Namespace):
    profile_name = args.profilename
    with JsonFiles(paths.user_json()) as user_json_obj:
        user_json_obj.set_value(profile_name, {})


def command_remove(args: argparse.Namespace):
    profile_name = args.profilename
    key = args.rmfromprofile
    with JsonFiles(paths.user_json()) as user_json_obj:
        if key is None:
            response = ""
            while not response in ["n", "y"]:
                response = input("Are you sure? (y/n): ")
            if response == "y":
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


def command_get(args: argparse.Namespace):
    profile_name: str = args.profilename
    key = args.key
    with JsonFiles(paths.user_json()) as user_json_obj:
        content: Dict = user_json_obj.get_value(profile_name)
        if key in content:
            print(content[key], file=stdout)
        else:
            print(None, file=stderr)


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


def main():
    profile_actions = {
        "add": command_add,
        "set": command_set,
        "get": command_get,
        "remove": command_remove,
        "show": command_show,
        "exec": command_exec,
        "get": command_get
    }

    wallet_actions = {"open": command_wallet, "close": command_closewallet}

    args = parse_args()
    if "profile_action" in args:
        profile_actions[args.profile_action](args)
        if args.verbose:
            command_show(args)
    elif "wallet_action" in args:
        wallet_actions[args.wallet_action](args)
    elif "list" in args:
        list_all_profiles()


if __name__ == "__main__":
    main()
