from pathlib import Path


def user_json() -> str:
    return "%s/.edtoken/user_data.json" % (Path.home())


def config() -> str:
    return "%s/.edtoken/config.json" % (Path.home())
