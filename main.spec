# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['src\\pyDXHR\\main.py'],
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

exe = EXE(
    a.scripts,
    [],
    exclude_binaries=True,
    entry_point='main:unpack_archive',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    [('build/*', 'build/')],
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
