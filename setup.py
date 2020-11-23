from setuptools import setup, find_packages
import os

MODULE_NAME = "getchwrap"
VERSIONFILE = os.path.join(os.path.dirname(__file__), MODULE_NAME, "_version.py")
exec(open(VERSIONFILE).read())

setup(
    name=MODULE_NAME,
    version=__version__,
    author="Ernesto Alfonso",
    author_email="erjoalgo@gmail.com",
    url="https://github.com/erjoalgo/getchwrap",
    description="A subprocess wrapper to ergonomically enhance tty user input",
    license="GPLv3",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "{0}={0}.{0}:main".format(MODULE_NAME)
        ]
    },
    install_requires=["pexpect"],
)
