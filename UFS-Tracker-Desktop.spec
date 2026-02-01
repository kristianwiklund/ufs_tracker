# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Collect webview data/binaries BEFORE Analysis, so they are passed in
# as raw 2-tuples alongside our own datas. Appending them to a.datas
# *after* Analysis runs fails because Analysis converts datas to 3-tuple
# TOC format internally — mixing 2-tuples into that list causes the
# "not enough values to unpack (expected 3, got 2)" crash in normalize_toc.
from PyInstaller.utils.hooks import collect_all
webview_datas, webview_binaries, webview_hiddenimports = collect_all('webview')

a = Analysis(
    ['desktop_app.py'],
    pathex=[],
    binaries=webview_binaries,
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('models', 'models'),
        ('services', 'services'),
        ('utils', 'utils'),
    ] + webview_datas,
    hiddenimports=[
        'flask',
        'requests',
        'bs4',
        'beautifulsoup4',
        'sqlite3',
        'argparse',
        'datetime',
        'json',
        'os',
        're',
        'webview',
        'webview.platforms.winforms',
        'models',
        'models.database',
        'services',
        'services.scraper',
        'utils',
        'utils.chart_parser',
    ] + webview_hiddenimports,
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
    [],
    name='UFS-Tracker-Desktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon=app.ico if you have an icon file
)
