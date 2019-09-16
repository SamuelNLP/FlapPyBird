from distutils.core import setup

setup(
    name="Flappy Bird",
    version="1.0",
    author="Sourabh Verma",
    windows=[{"script": "flappy.py", "icon_resources": [(1, "flappy.ico")]}],
    zipfile=None,
)
