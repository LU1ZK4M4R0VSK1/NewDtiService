import subprocess
import platform
import os
import shlex
import shutil
import time
from ..utils.constants import AppConfig

class ScriptRunnerService:
    @staticmethod
    def _build_windows_startup_kwargs():
        kwargs = {}
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        kwargs["startupinfo"] = startupinfo
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        return kwargs

    @staticmethod
    def _expand_path(raw_path: str) -> str:
        expanded = os.path.expandvars(os.path.expanduser(raw_path.strip().strip('"')))
        if not os.path.isabs(expanded):
            expanded = os.path.abspath(expanded)
        return expanded

    @staticmethod
    def _extract_script_and_args(script_command: str):
        raw = (script_command or "").strip()
        if not raw:
            return None, []

        direct_candidate = ScriptRunnerService._expand_path(raw)
        if os.path.exists(direct_candidate):
            return direct_candidate, []

        try:
            tokens = shlex.split(raw, posix=False)
        except ValueError:
            tokens = [raw]

        if not tokens:
            return None, []

        for end in range(len(tokens), 0, -1):
            candidate_raw = " ".join(tokens[:end])
            candidate = ScriptRunnerService._expand_path(candidate_raw)
            if os.path.exists(candidate):
                return candidate, tokens[end:]

        return ScriptRunnerService._expand_path(tokens[0]), tokens[1:]

    @staticmethod
    def run_script(script_command: str, on_output=None):
        system = platform.system()

        script_path, script_args = ScriptRunnerService._extract_script_and_args(script_command)
        if not script_path:
            return False, "Caminho do script vazio."

        if not os.path.exists(script_path):
            return False, "Arquivo não encontrado."

        working_dir = os.path.dirname(script_path) or os.getcwd()
        timeout_seconds = AppConfig.SCRIPT_TIMEOUT_SECONDS

        try:
            cmd = []
            popen_extra = {}
            if system == "Windows":
                shell_executable = shutil.which("pwsh") or shutil.which("powershell") or "powershell"
                cmd = [
                    shell_executable,
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    script_path,
                    *script_args,
                ]
                popen_extra = ScriptRunnerService._build_windows_startup_kwargs()
            else:
                if script_path.lower().endswith(".ps1"):
                    shell_executable = shutil.which("pwsh")
                    if not shell_executable:
                        return False, "PowerShell 7 (pwsh) não encontrado para executar .ps1 neste sistema."
                    cmd = [
                        shell_executable,
                        "-NoLogo",
                        "-NoProfile",
                        "-NonInteractive",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        script_path,
                        *script_args,
                    ]
                else:
                    cmd = ["/bin/bash", script_path, *script_args]

            env = os.environ.copy()

            if on_output:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1,
                    cwd=working_dir,
                    env=env,
                    **popen_extra,
                )

                chunks = []
                started = time.monotonic()

                while True:
                    if time.monotonic() - started > timeout_seconds:
                        proc.kill()
                        partial = "".join(chunks).strip()
                        timeout_msg = [
                            f"Timeout após {timeout_seconds}s.",
                            f"Diretório: {working_dir}",
                            "Dica: para scripts de otimização longos, aumente AppConfig.SCRIPT_TIMEOUT_SECONDS.",
                        ]
                        if partial:
                            timeout_msg.append(f"Saída parcial: {partial}")
                        return False, "\n".join(timeout_msg)

                    if proc.stdout is None:
                        break

                    line = proc.stdout.readline()
                    if line:
                        chunks.append(line)
                        on_output(line)
                        continue

                    if proc.poll() is not None:
                        break

                if proc.stdout is not None:
                    tail = proc.stdout.read()
                    if tail:
                        chunks.append(tail)
                        on_output(tail)

                return_code = proc.wait()
                combined = "".join(chunks).strip()

                if return_code == 0:
                    return True, combined or "Comando concluído sem saída."

                details = [
                    f"Exit code: {return_code}",
                    f"Diretório: {working_dir}",
                ]
                if combined:
                    details.append(f"Saída: {combined}")
                return False, "\n".join(details)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                cwd=working_dir,
                env=env,
                **popen_extra,
            )

            stdout = (result.stdout or "").strip()
            stderr = (result.stderr or "").strip()

            if result.returncode == 0:
                output = stdout or "Comando concluído sem saída."
                return True, output
            else:
                details = [
                    f"Exit code: {result.returncode}",
                    f"Diretório: {working_dir}",
                ]
                if stderr:
                    details.append(f"Erro: {stderr}")
                if stdout:
                    details.append(f"Saída: {stdout}")
                return False, "\n".join(details)

        except subprocess.TimeoutExpired as e:
            partial_out = (e.stdout or "") if isinstance(e.stdout, str) else ""
            partial_err = (e.stderr or "") if isinstance(e.stderr, str) else ""
            timeout_msg = [
                f"Timeout após {timeout_seconds}s.",
                f"Diretório: {working_dir}",
                "Dica: para scripts de otimização longos, aumente AppConfig.SCRIPT_TIMEOUT_SECONDS.",
            ]
            if partial_err.strip():
                timeout_msg.append(f"Saída parcial (erro): {partial_err.strip()}")
            elif partial_out.strip():
                timeout_msg.append(f"Saída parcial: {partial_out.strip()}")
            return False, "\n".join(timeout_msg)
        except Exception as e:
            return False, str(e)