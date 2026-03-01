import os
import sys
import shutil
import subprocess

from src.utils.constants import AppConfig

SHORTCUT_PATH = r"C:\Users\Public\Desktop\DTI Service.lnk"
ICO_FILENAME = "dti_service.ico"
LOG_PATH = os.path.join(AppConfig.BASE_DIR, "shortcut_debug.log")


def _log(msg: str):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def _get_exe_path() -> str:
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        return os.path.abspath("main.py")


def _get_ico_path() -> str:
    """
    Copia o .ico original (multi-resolução) do _MEIPASS para ao lado do exe.
    Sempre sobrescreve para garantir que versões antigas não fiquem cacheadas.
    """
    dest = os.path.join(AppConfig.BASE_DIR, ICO_FILENAME)

    if getattr(sys, 'frozen', False):
        # Candidatos no bundle PyInstaller
        candidates = [
            os.path.join(sys._MEIPASS, "src", "assets", ICO_FILENAME),
            os.path.join(sys._MEIPASS, "assets", ICO_FILENAME),
            os.path.join(sys._MEIPASS, ICO_FILENAME),
        ]
        _log(f"[ico] BASE_DIR:   {AppConfig.BASE_DIR}")
        _log(f"[ico] _MEIPASS:   {sys._MEIPASS}")
        _log(f"[ico] dest:       {dest}")

        for src_ico in candidates:
            exists = os.path.exists(src_ico)
            size   = os.path.getsize(src_ico) if exists else 0
            _log(f"[ico] candidate: {src_ico} | exists={exists} | size={size}b")
            if exists:
                shutil.copy2(src_ico, dest)
                _log(f"[ico] copiado! dest size={os.path.getsize(dest)}b")
                return dest

        # Fallback: usa o próprio exe como fonte de ícone
        _log("[ico] FALLBACK: nenhum candidate encontrado, usando exe,0")
        return f"{_get_exe_path()},0"
    else:
        return os.path.abspath(os.path.join("src", "assets", ICO_FILENAME))


def shortcut_exists() -> bool:
    return os.path.exists(SHORTCUT_PATH)


def create_admin_shortcut():
    exe_path = _get_exe_path()
    ico_path = _get_ico_path()

    # Garante ,0 no final se não for fallback (que já inclui o índice)
    if not ico_path.endswith(",0"):
        icon_location = f"{ico_path},0"
    else:
        icon_location = ico_path

    _log(f"[shortcut] exe:       {exe_path}")
    _log(f"[shortcut] icon_loc:  {icon_location}")

    exe_ps  = exe_path.replace("'", "''")
    icon_ps = icon_location.replace("'", "''")
    lnk_ps  = SHORTCUT_PATH.replace("'", "''")

    ps_script = f"""
if (Test-Path '{lnk_ps}') {{ Remove-Item '{lnk_ps}' -Force }}

$WshShell   = New-Object -ComObject WScript.Shell
$Shortcut   = $WshShell.CreateShortcut('{lnk_ps}')
$Shortcut.TargetPath   = '{exe_ps}'
$Shortcut.IconLocation = '{icon_ps}'
$Shortcut.Description  = 'DTI Service - Apenas para Administradores'
$Shortcut.Save()

Write-Output "Atalho criado OK"
"""

    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True, text=True, timeout=30
        )
        _log(f"[ps] returncode={result.returncode}")
        _log(f"[ps] stdout={result.stdout.strip()}")
        if result.returncode != 0:
            _log(f"[ps] stderr={result.stderr.strip()}")
    except Exception as e:
        _log(f"[ps] Exceção: {e}")
