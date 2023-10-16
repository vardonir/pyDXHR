# TODO

from setuptools import setup, find_packages

setup(
    name="pyDXHR",
    version="0.1.0",
    description="A Python library for reading and writing Deus Ex: Human Revolution files",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "bigfile = pyDXHR.entrypoints:bigfile",
            "drm = pyDXHR.entrypoints:drm",
        ]
    }
)
