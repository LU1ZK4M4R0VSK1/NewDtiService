# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

flet_desktop_datas = collect_data_files("flet_desktop", includes=["app/**/*"])
flet_datas = collect_data_files("flet")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/assets', 'src/assets'), *flet_desktop_datas, *flet_datas],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DTI Service',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=None,
    uac_admin=True,
    icon=['src\\assets\\dti_service_v2.ico'],
)
