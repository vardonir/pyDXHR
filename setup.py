from setuptools import setup, find_packages

setup(
    name="pyDXHR",
    version="1.0.0",
    packages=find_packages(),
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
