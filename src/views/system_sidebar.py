import flet as ft
import threading
import time
from src.viewmodels.system_vm import SystemViewModel
from src.utils.constants import ThemeColors

class SystemSidebar(ft.Container):
    def __init__(self):
        super().__init__(
            width=280,
            padding=20,
            bgcolor=ThemeColors.SURFACE,
            # Borda direita para separar do conteúdo principal
            border=ft.border.only(right=ft.BorderSide(1, ThemeColors.PRIMARY)),
        )
        self.vm = SystemViewModel()
        self.running = True
        
        # --- Componentes de Identificação ---
        self.logo = ft.Image(
            src="logo_itambe.png",
            width=180,
            height=90,
            fit=ft.ImageFit.CONTAIN,
        )
        
        self.user_text = ft.Text("Usuário: --", size=12, color=ThemeColors.PRIMARY)
        self.host_text = ft.Text("Máquina: --", size=12, color=ThemeColors.DISABLED)
        self.ip_text = ft.Text("IP: --", size=12, color=ThemeColors.DISABLED)
        self.local_text = ft.Text("Local: --", size=14, weight="bold", color=ThemeColors.SECONDARY)
        
        # Componente de Rede (Ícone + Texto)
        self.conn_icon = ft.Icon(ft.Icons.LAN, size=16, color=ThemeColors.DISABLED)
        self.conn_text = ft.Text("Rede: --", size=12, color=ThemeColors.DISABLED)
        self.conn_row = ft.Row([self.conn_icon, self.conn_text], spacing=5)

        # --- Gráficos de Performance ---
        self.cpu_text = ft.Text("CPU: --", font_family="Consolas", size=12)
        self.cpu_bar = ft.ProgressBar(value=0, color=ThemeColors.PRIMARY, bgcolor="#222222")
        
        self.ram_text = ft.Text("RAM: --", font_family="Consolas", size=12)
        self.ram_bar = ft.ProgressBar(value=0, color=ThemeColors.SECONDARY, bgcolor="#222222")
        
        self.disk_text = ft.Text("Disco: --", font_family="Consolas", size=11)
        self.disk_bar = ft.ProgressBar(value=0, color=ft.Colors.AMBER, bgcolor="#222222")

        # Organização do Conteúdo
        self.content = ft.Column([
            ft.Container(content=self.logo, alignment=ft.alignment.center, padding=ft.padding.only(bottom=10)),
            
            ft.Text("SYSTEM MONITOR", weight="bold", size=16, color=ThemeColors.PRIMARY),
            ft.Divider(color=ThemeColors.PRIMARY, height=1),
            
            ft.Column([
                self.local_text,
                self.conn_row,
                self.user_text,
                self.host_text,
                self.ip_text,
            ], spacing=4),
            
            ft.Divider(height=20, color="transparent"),
            
            self.cpu_text, self.cpu_bar,
            ft.Divider(height=5, color="transparent"),
            self.ram_text, self.ram_bar,
            ft.Divider(height=5, color="transparent"),
            self.disk_text, self.disk_bar,
        ], spacing=10, scroll=ft.ScrollMode.ADAPTIVE)

    def did_mount(self):
        self.running = True
        self.th = threading.Thread(target=self.update_stats, daemon=True)
        self.th.start()

    def will_unmount(self):
        self.running = False

    def update_stats(self):
        while self.running:
            try:
                data = self.vm.get_stats()
                if data and "error" not in data:
                    ip = data.get('ip', '0.0.0.0')
                    
                    # Lógica de Rede Inteligente
                    octetos = ip.split('.')
                    if len(octetos) >= 3:
                        third_octet = octetos[2]
                        # Regra: 10.XX.1X = Cabo | 10.XX.2X = Wifi
                        if third_octet.startswith("1"):
                            self.conn_icon.name, self.conn_text.value = ft.Icons.LAN, "Rede: Cabeada"
                            self.conn_icon.color = ThemeColors.PRIMARY
                        elif third_octet.startswith("2"):
                            self.conn_icon.name, self.conn_text.value = ft.Icons.WIFI, "Rede: Wi-Fi"
                            self.conn_icon.color = ft.Colors.BLUE_400
                        else:
                            self.conn_icon.name, self.conn_text.value = ft.Icons.NETWORKING_SATELLITE, "Rede: Outra"

                    # Atualização da Interface
                    self.user_text.value = f"Usuário: {data['user']}"
                    self.host_text.value = f"Máquina: {data['machine']}"
                    self.ip_text.value = f"IP: {ip}"
                    self.local_text.value = f"📍 {data['local']}"
                    self.cpu_text.value = f"CPU: {data['cpu_percent']}%"
                    self.cpu_bar.value = data['cpu_percent'] / 100
                    self.ram_text.value = f"RAM: {data['ram_percent']}%"
                    self.ram_bar.value = data['ram_percent'] / 100
                    self.disk_text.value = f"Disco: {data['disk_info']}"
                    self.disk_bar.value = data['disk_percent'] / 100
                    
                    self.update()
                time.sleep(2)
            except Exception as e:
                print(f"Erro no monitor: {e}")
                break