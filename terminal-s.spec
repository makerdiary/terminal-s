# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['terminal_s\\terminal.py'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter', 'lib2to3', 'ssl', 'bz2', 'lzma', 'curses'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
excluded_binaries = ['libcrypto-1_1.dll']
a.binaries = TOC([x for x in a.binaries if x[0] not in excluded_binaries])
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='terminal-s',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True)
