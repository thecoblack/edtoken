from os import mkdir
from pathlib import Path

from setuptools import setup

directories = ["/.edtoken"]
for directory in directories:
    path = "%s%s" % (Path.home(), directory)
    if not Path(path).exists():
        print("Directory created: %s" % (path))
        mkdir(path)

files = ["/.edtoken/user_data.json", "/.edtoken/config.json"]
for _file in files:
    path = "%s%s" % (Path.home(), _file)
    if not Path(path).exists():
        print("File created: %s" % (path))
        with open(path, "w") as f:
            f.write("{}")

with open("requirements.txt", "r") as f:
    requirements = f.read().split("\n")

with open("VERSION", "r") as f:
    version = f.read().strip()
    print(version)

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="edtoken",
    long_description=long_description,
    version=version,
    license="MIT",
    long_description_content_type="text/markdown",
    author="thecoblack",
    url="https://github.com/thecoblack/edtoken",
    install_requires=requirements,
    packages=["ed_token", "ed_token.utils"],
    classifiers=["Programming Language :: Python :: 3.8"],
    python_requires=">=3.8",
    entry_points={"console_scripts": "edtoken=ed_token.__init__:main"},
)
