import os
import sys
import shutil
import subprocess

from src.utils.constants import AppConfig

SHORTCUT_PATH = r"C:\Users\Public\Desktop\DTI Service.lnk"
ICO_FILENAME = "dti_service_v2.ico"
# LOG_PATH moved to local TEMP to avoid permissions/UNC issues when running from network
temp_dir = os.environ.get("TEMP", os.environ.get("TMP", "C:\\Temp"))
LOG_PATH = os.path.join(temp_dir, "shortcut_debug.log")


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
    Copia o .ico para um diretório PÚBLICO (%PROGRAMDATA%\\DTIService\\).
    Isso é necessário porque o atalho é criado no Desktop Público, e se o ícone
    estiver no AppData privado de um usuário, outros (ou o sistema) não o verão.
    """
    # Destino público e local — visível para todos os perfis
    local_dir = os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "DTIService")
    os.makedirs(local_dir, exist_ok=True)
    dest = os.path.join(local_dir, ICO_FILENAME)

    if getattr(sys, 'frozen', False):
        # Candidatos no bundle PyInstaller
        candidates = [
            os.path.join(sys._MEIPASS, "src", "assets", ICO_FILENAME),
            os.path.join(sys._MEIPASS, "assets", ICO_FILENAME),
            os.path.join(sys._MEIPASS, ICO_FILENAME),
        ]
        _log(f"[ico] local_dir:  {local_dir}")
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

        # Fallback: usa o próprio exe como fonte de ícone (pode não aparecer em UNC)
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
    # Windows handles .ico files directly; removal of ,0 for better stability
    icon_location = ico_path

    _log(f"[shortcut] exe:       {exe_path}")
    _log(f"[shortcut] icon_loc:  {icon_location}")

    exe_ps  = exe_path.replace("'", "''")
    icon_ps = icon_location.replace("'", "''")
    lnk_ps  = SHORTCUT_PATH.replace("'", "''")

    ps_script = f"""
if (Test-Path '{lnk_ps}') {{ Remove-Item '{lnk_ps}' -Force }}

# Desbloqueia o ícone se ele tiver sido baixado/copiado da rede
Unblock-File -Path '{icon_ps.split(',')[0]}' -ErrorAction SilentlyContinue

$WshShell   = New-Object -ComObject WScript.Shell
$Shortcut   = $WshShell.CreateShortcut('{lnk_ps}')
$Shortcut.TargetPath   = '{exe_ps}'
$Shortcut.IconLocation = '{icon_ps}'
$Shortcut.Description  = 'DTI Service - Apenas para Administradores'
$Shortcut.Save()

# Força a atualização do Shell (Desktop) para que o ícone apareça imediatamente
try {{
    # 1. Refresh via Shell.Application COM
    (New-Object -ComObject Shell.Application).Namespace(0).Self.InvokeVerb("refresh")
    # 2. Rebuild icon cache (Windows standard)
    Start-Process "ie4uinit.exe" -ArgumentList "-show" -Wait -ErrorAction SilentlyContinue
    # 3. Notifica o sistema de mudanças no shell
    $code = '[DllImport("shell32.dll")] public static extern void SHChangeNotify(int wEventId, int uFlags, IntPtr dwItem1, IntPtr dwItem2);'
    Add-Type -MemberDefinition $code -Namespace Win32 -Name Shell
    [Win32.Shell]::SHChangeNotify(0x08000000, 0x0000, [IntPtr]::Zero, [IntPtr]::Zero)
}} catch {{}}

Write-Output "Atalho e ícone atualizados"
"""

    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0

        # Force a local working directory (C:\) to avoid "UNC paths are not supported" errors in PowerShell
        result = subprocess.run(
            ["powershell", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True, text=True, timeout=30,
            cwd="C:\\",
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        _log(f"[ps] returncode={result.returncode}")
        _log(f"[ps] stdout={result.stdout.strip()}")
        if result.returncode != 0:
            _log(f"[ps] stderr={result.stderr.strip()}")
    except Exception as e:
        _log(f"[ps] Exceção: {e}")
