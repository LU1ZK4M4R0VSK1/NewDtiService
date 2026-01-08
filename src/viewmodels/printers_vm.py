from src.services.printer_service import PrinterService

class PrintersViewModel:
    def __init__(self):
        self.service = PrinterService()

    def format_number(self, number: str) -> str:
        """Formata o número para 4 dígitos (ex: 1 -> 0001)."""
        return f"{int(number):04d}"

    def get_path(self, number: str) -> str:
        """Determina o servidor baseado na faixa do número."""
        num_int = int(number)
        num_str = self.format_number(number)
        
        # Lógica de servidores (Narnia vs Prtsrv-fabrica)
        if 601 <= num_int <= 701:
            return f"\\\\prtsrv-fabrica\\IMP-{num_str}"
        else:
            return f"\\\\nirvana\\IMP-{num_str}"

    def process_install(self, raw_input: str):
        """Processa a string (ex: '102, 605') e instala todas."""
        if not raw_input:
            return False, "Digite ao menos um número."

        numbers = [n.strip() for n in raw_input.split(',')]
        installed_count = 0
        errors = []

        for n in numbers:
            if n.isdigit() and 0 <= int(n) <= 9999:
                path = self.get_path(n)
                if self.service.install_printer_connection(path):
                    installed_count += 1
            else:
                errors.append(n)

        if errors:
            return False, f"Erro nos números: {', '.join(errors)}"
        
        return True, f"{installed_count} impressora(s) enviada(s) para instalação."