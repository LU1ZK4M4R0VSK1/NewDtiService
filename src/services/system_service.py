import flet as ft
import psutil
import socket
import platform
import os
import getpass

class SystemInfoService:
    def get_local_info(self, ip: str) -> str:
        filial_mapping = {
            "0": "SEDE", "15": "FÁBRICA", "1": "CIC", "2": "COLOMBO", "3": "PARANAGUÁ",
            "4": "PONTA GROSSA", "5": "CAMBÉ", "6": "BLUMENAU", "7": "FLORIANÓPOLIS",
            "8": "ITAJAÍ", "9": "JOINVILLE", "10": "MARINGÁ", "11": "SÃO JOSÉ",
            "12": "CAMBORIU", "13": "CD ITAJAI", "14": "CD CASCAVEL", "16": "MINA",
            "17": "ARAQUARI"
        }
        try:
            # Pega o segundo octeto do IP (ex: 10.15.x.x -> 15)
            second_octet = ip.split(".")[1]
            return filial_mapping.get(second_octet, "Filial desconhecida")
        except:
            return "IP Inválido"
        
    def get_connection_type(self, ip: str) -> tuple[str, str]:
        """Retorna o tipo de conexão e o ícone correspondente."""
        try:
            # Analisa o terceiro octeto: 10.XX.YY.XXX
            third_octet = ip.split(".")[2]
            
            # Se o terceiro octeto começa com 1 (ex: 10, 11, 15...) é cabeado
            # Se o terceiro octeto começa com 2 (ex: 20, 21, 25...) é wifi
            if third_octet.startswith("1"):
                return "Cabeada", ft.Icons.LAN
            elif third_octet.startswith("2"):
                return "Wi-Fi", ft.Icons.WIFI
            else:
                return "Desconhecida", ft.Icons.HELP_OUTLINE
        except:
            return "Erro", ft.Icons.ERROR_OUTLINE

    def get_system_info(self):
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            
            # Cálculo de disco (Compatível com Windows C:/)
            disk = psutil.disk_usage('C:/' if os.name == 'nt' else '/')
            disk_info = f"{disk.used / (1024 ** 3):.2f} GB de {disk.total / (1024 ** 3):.2f} GB"

            return {
                "user": getpass.getuser(),
                "machine": hostname,
                "ip": ip,
                "local": self.get_local_info(ip),
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "ram_percent": psutil.virtual_memory().percent,
                "disk_info": disk_info,
                "disk_percent": disk.percent
            }
        except Exception as e:
            return {"error": str(e)}