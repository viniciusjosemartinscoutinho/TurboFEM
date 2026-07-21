# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [
    ('argos_packages', 'argos_packages'),
    ('Fast-FEA-Logo.png', '.'),
    ('keys.txt', '.'),
    ('Planning', 'Planning'),
    ('Solvers\\S1\\calculix\\CalculiX-2.23.0-win-x64\\bin', 'Solvers\\S1\\calculix\\CalculiX-2.23.0-win-x64\\bin'),
]
binaries = []
hiddenimports = []

tmp_ret = collect_all('PySide6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('argostranslate')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('ctranslate2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('stanza')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('sentencepiece')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Remove qualquer stub/arquivo solto de "triton" que os collect_all() tenham
# trazido como dado (não como import de verdade) — ele quebra dentro do .exe
# empacotado (ImportError: attempted relative import with no known parent package).
# Isso cobre o que ENTROU via collect_all acima.
datas = [d for d in datas if 'triton' not in d[0].replace('\\', '/').lower()]
binaries = [b for b in binaries if 'triton' not in b[0].replace('\\', '/').lower()]
hiddenimports = [h for h in hiddenimports if 'triton' not in h.lower()]

a = Analysis(
    ['main_TurboFEM_versions.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['triton'],
    noarchive=False,
    optimize=0,
)

# IMPORTANTE: o hook interno do PyInstaller para 'torch' (hook-torch.py) roda
# DENTRO do Analysis() acima (disparado porque stanza -> torch é detectado na
# análise de imports) e injeta um stub "triton.py" direto em a.datas/a.binaries
# DEPOIS que o Analysis já processou tudo. Por isso o filtro de cima (que age
# nas listas datas/binaries/hiddenimports de ANTES do Analysis) não pega esse
# arquivo -- ele só existe a partir daqui. Filtra de novo, agora em cima do
# resultado real do Analysis.
a.datas = [d for d in a.datas if 'triton' not in d[0].replace('\\', '/').lower()]
a.binaries = [b for b in a.binaries if 'triton' not in b[0].replace('\\', '/').lower()]
a.pure = [p for p in a.pure if not (p[0] == 'triton' or p[0].startswith('triton.'))]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TurboFEM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console= False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Fast-FEA-Logo.ico',
)
