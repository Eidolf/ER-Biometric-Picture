
# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect InsightFace and OnnxRuntime dependencies if needed
# Collect InsightFace and OnnxRuntime dependencies if needed
datas = []
datas += collect_data_files('insightface')
datas += collect_data_files('onnxruntime')

# Explicitly collect 'app' package ensuring all submodules are found
# This handles "ModuleNotFoundError: No module named 'app.ui'"
hidden_app = collect_submodules('app')

# Add config.yaml
datas += [('app/config.yaml', 'app'), ('images/logo.png', 'images')]

a = Analysis(
    ['app/main.py'],
    pathex=['.'], # Ensure root is in path so 'app' module is resolved
    binaries=[],
    datas=datas,
    hiddenimports=['sklearn.utils._typedefs', 'sklearn.neighbors._partition_nodes', 'scipy.special.cython_special'] + hidden_app,
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
    [],
    exclude_binaries=True,
    name='PassPhotoCheck',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None # 'images/logo.png' # Setup icon if .ico available, else png might fail on Windows
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PassPhotoCheck',
)
