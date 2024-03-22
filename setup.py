from setuptools import setup, find_packages

setup(
    name="pyDXHR",
    version="1.0.0",
    packages=find_packages(),
    description="Collection of tools for working with Deus Ex: Human Revolution's game files",
    long_description="See pydxhr.vardonir.com for more information",
    author="Vardonir",
    entry_points={
        "console_scripts": [
            "bigfile = pyDXHR.entrypoints:bigfile",
            "drm = pyDXHR.entrypoints:drm",
            "unit = pyDXHR.entrypoints:unit",
            "gltf = pyDXHR.entrypoints:gltf",
            "usm = pyDXHR.entrypoints:usm",
        ]
    }
)
