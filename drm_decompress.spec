# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['src\\pyDXHR\\drm_decompress.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='drm_decompress',
    debug=False,
    strip=False,
    upx=True,
    console=True,
)
