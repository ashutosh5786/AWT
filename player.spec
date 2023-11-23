# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['player.py'],
    pathex=[],
    binaries=[],
    datas=[('./backward.png', '.'), ('./default_album_art.png', '.'), ('./forward.png', '.'), ('./mute.png', '.'), ('./pause.png', '.'), ('./play.png', '.'), ('./repeat.png', '.'), ('./repeat_once.png', '.'), ('./shuffle.png', '.'), ('./stop.png', '.'), ('./unmute.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='player',
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
)
