"""
Tests for the Bigfile class.
The env must be set correctly for these tests to pass - it assumes that you have the PC version of HR: Director's Cut,
installed somewhere (or just have the bigfiles, the .exe is not important), and the path configured in the .env file.
Since the files are large, they are not included in the repository, and the tests might take more than a few seconds.

If you don't have the game installed, only the test_from_env test will pass.
"""

import pytest
from pyDXHR.Bigfile import Bigfile


def test_from_env(monkeypatch):
    monkeypatch.setenv('version', 'tml')
    monkeypatch.setenv('platform', 'pc')

    bf = Bigfile.from_env()
    assert bf.version == Bigfile.Version.MISSING_LINK
    assert bf.platform == Bigfile.Platform.PC


@pytest.fixture
def bigfile_from_env():
    bf = Bigfile.from_env()
    bf.open()
    return bf


def test_named_entries(bigfile_from_env):
    """ As of 2023 August, the filelist for DXHRDC has 101,216 named entries """
    assert len(bigfile_from_env.named_entries) == 101216


def test_unknown_entries(bigfile_from_env):
    assert len(bigfile_from_env.unknown_entries) == 2156


def test_platform(bigfile_from_env):
    assert bigfile_from_env.platform == Bigfile.Platform.PC
