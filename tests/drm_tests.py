"""
Tests for the DRM class.
The provided test file is an unknown file obtained from the base PC version of the game. The file also exists in the
DC version, but it's not the exact same file (DC version is bigger).
"""

import os
import pytest
from pyDXHR.DRM import DRM


@pytest.fixture
def drm_path():
    return os.path.join(os.path.dirname(__file__), 'AB0AD4A3.drm')


@pytest.fixture
def drm_bytes():
    file = os.path.join(os.path.dirname(__file__), 'AB0AD4A3.drm')
    with open(file, 'rb') as f:
        return f.read()


def test_from_file(drm_path):
    drm = DRM.from_file(drm_path)
    assert isinstance(drm, DRM)
    assert len(drm.decompressed_bytes) > 0


def test_from_bytes(drm_bytes):
    drm = DRM.from_bytes(drm_bytes)
    assert isinstance(drm, DRM)
    assert len(drm.decompressed_bytes) > 0


def test_header_open(drm_path):
    drm = DRM.from_file(drm_path)
    drm.open()


def test_header_read(drm_path):
    drm = DRM.from_file(drm_path)
    drm.open()
    assert len(drm.drm_deps) == 72
    assert len(drm.obj_deps) == 0
    assert drm.root_section_index == 0xFFFFFFFF
