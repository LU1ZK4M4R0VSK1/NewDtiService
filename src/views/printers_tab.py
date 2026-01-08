import flet as ft
from src.utils.constants import ThemeColors
from src.views.components.cyber_card import CyberCard
from src.viewmodels.printers_vm import PrintersViewModel

class PrintersTab(ft.Container):
    def __init__(self):
        super().__init__(expand=True, padding=20)
        self.vm = PrintersViewModel()
        
        # Campo de entrada com suporte a múltiplos números
        self.printer_input = ft.TextField(
            label="Números das Impressoras (ex: 102, 605)",
            hint_text="Separe por vírgula para instalar várias",
            border_color=ThemeColors.PRIMARY,
            focused_border_color=ThemeColors.PRIMARY,
            width=400,
            text_align=ft.TextAlign.CENTER,
            on_submit=lambda _: self.handle_install()
        )

        self.content = ft.Column([
            ft.Text("GESTÃO DE IMPRESSORAS", size=24, weight="bold", color=ThemeColors.PRIMARY),
            # CORREÇÃO: Usando Divider em vez de VerticalDivider para espaçamento vertical
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            
            ft.Row([
                CyberCard(
                    ft.Column([
                        ft.Icon(
                            ft.Icons.PRINT_ROUNDED, 
                            size=100, 
                            color=ThemeColors.PRIMARY,
                        ),
                        ft.Text("INSTALADOR DE REDE", size=18, weight="bold"),
                        ft.Text(
                            "Insira os números da(s) impressoras\nServidores: \\\\nirvana e \\\\prtsrv-fabrica",
                            text_align=ft.TextAlign.CENTER,
                            color=ThemeColors.DISABLED
                        ),
                        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                        self.printer_input,
                        ft.ElevatedButton(
                            "INSTALAR IMPRESSORA(S)",
                            icon=ft.Icons.DOWNLOAD_ROUNDED,
                            bgcolor=ThemeColors.PRIMARY,
                            color="black",
                            height=50,
                            on_click=lambda _: self.handle_install()
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.START)

    def handle_install(self):
        if not self.printer_input.value:
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Por favor, digite um número.")))
            return

        success, message = self.vm.process_install(self.printer_input.value)
        
        color = "green" if success else "red"
        self.page.show_snack_bar(
            ft.SnackBar(ft.Text(message), bgcolor=color)
        )
        if success:
            self.printer_input.value = ""
            self.update()