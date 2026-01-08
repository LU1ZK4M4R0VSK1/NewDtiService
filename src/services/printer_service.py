import os
import subprocess
import platform

class PrinterService:
    def install_printer_connection(self, path: str) -> bool:
        """Tenta abrir a conexão com a impressora de rede."""
        try:
            if platform.system() == "Windows":
                # os.startfile é mais silencioso e nativo para caminhos UNC
                os.startfile(path)
            else:
                # Fallback para outros sistemas (principalmente para testes)
                subprocess.run(['explorer', path] if platform.system() == "Windows" else ['xdg-open', path])
            return True
        except Exception as e:
            print(f"Erro ao acessar caminho {path}: {e}")
            return False