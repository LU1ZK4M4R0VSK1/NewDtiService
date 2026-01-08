import subprocess
import platform
import os

class ScriptRunnerService:
    @staticmethod
    def run_script(script_path: str):
        system = platform.system()
        
        if not os.path.exists(script_path):
            return False, "Arquivo não encontrado."

        try:
            if system == "Windows":
                # Executa PowerShell
                cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path]
            else:
                # Executa Bash (Linux/Mac)
                cmd = ["/bin/bash", script_path]

            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr

        except subprocess.TimeoutExpired:
            return False, "Timeout: A execução demorou muito."
        except Exception as e:
            return False, str(e)