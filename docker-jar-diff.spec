# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['docker_jar_diff/cli.py'],
    pathex=[],
    binaries=[],
    datas=[('D:/resource/python/docker-jar-diff/.config/config.json', '.config')],
    hiddenimports=['docker', 'click', 'docker.api', 'docker.api.build', 'docker.api.client', 'docker.api.container', 'docker.api.daemon', 'docker.api.exec_api', 'docker.api.image', 'docker.api.network', 'docker.api.plugin', 'docker.api.secret', 'docker.api.service', 'docker.api.swarm', 'docker.api.volume', 'docker.auth', 'docker.client', 'docker.constants', 'docker.errors', 'docker.models', 'docker.models.containers', 'docker.models.images', 'docker.models.networks', 'docker.models.nodes', 'docker.models.secrets', 'docker.models.services', 'docker.models.swarm', 'docker.models.volumes', 'docker.tls', 'docker.types', 'docker.types.base', 'docker.types.daemon', 'docker.types.services', 'docker.types.swarm', 'docker.utils', 'docker.utils.build', 'docker.utils.config', 'docker.utils.ports', 'docker.utils.proxy', 'docker.utils.socket', 'docker.utils.utils', 'requests', 'urllib3', 'click', 'json', 'os', 'sys', 'time', 'shutil', 'tempfile', 'zipfile', 'tarfile'],
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
    [],
    exclude_binaries=True,
    name='docker-jar-diff',
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
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='docker-jar-diff',
)
