import flet as ft
from src.utils.constants import ThemeColors
from src.viewmodels.tickets_vm import TicketsViewModel

class TicketsPopup:
    def __init__(self, page: ft.Page):
        self.page = page
        self.vm = TicketsViewModel()
        
        # Estilo para os campos
        self.field_style = {
            "border_color": ThemeColors.SECONDARY,
            "focused_border_color": ThemeColors.SECONDARY,
            "label_style": ft.TextStyle(color=ThemeColors.SECONDARY),
            "border_radius": 8,
            "bgcolor": "#1A1A1A",
            "content_padding": ft.padding.all(15), # Resolve sobreposição interna
            "text_size": 14,
        }

        self.comentario_input = ft.TextField(
            label="Comentários",
            multiline=True,
            min_lines=3,
            **self.field_style
        )

        # Dropdown de Categorias
        self.categoria_dropdown = ft.Dropdown(
            label="Categoria",
            hint_text="Selecione...",
            **self.field_style,
            options=[
                ft.dropdown.Option("Suporte a Impressao"),
                ft.dropdown.Option("Instalacao de software"),
                ft.dropdown.Option("Suporte a sistemas"),
                ft.dropdown.Option("Suporte a Internet"),
                ft.dropdown.Option("Autenticacao"),
                ft.dropdown.Option("Orientacao a Usuario"),
                ft.dropdown.Option("Suporte a Equipamentos de TI"),
                ft.dropdown.Option("Otimizacao")
            ],
        )

        self.status_dropdown = ft.Dropdown(
            label="Status",
            hint_text="Selecione...",
            **self.field_style,
            options=[
                ft.dropdown.Option("Concluido"),
                ft.dropdown.Option("A Fazer")
            ],
        )

        # Dropdown de Atendentes com a lista fornecida
        atendentes_list = [
            "rafael.leal", "luiz.kamarovski", "emerson.duda",
            "diego.surgik", "andre.santos", "alfredo.silva", "cristiano.citero"
        ]
        
        self.atendente_dropdown = ft.Dropdown(
            label="Atendente",
            hint_text="Selecione...",
            **self.field_style,
            options=[ft.dropdown.Option(nome) for nome in atendentes_list],
        )

    def open(self, e=None):
        self.comentario_input.value = ""
        self.comentario_input.error_text = None
        
        modal = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.CONFIRMATION_NUMBER_OUTLINED, color=ThemeColors.SECONDARY),
                ft.Text("NOVO CHAMADO DTI", color=ThemeColors.SECONDARY, weight="bold")
            ], spacing=10),
            bgcolor="#111111",
            content=ft.Column([
                ft.Text(f"Solicitante: {self.vm.get_logged_in_user()}", color=ThemeColors.DISABLED, size=11),
                self.comentario_input,
                ft.Row([
                    ft.Container(self.categoria_dropdown, expand=1),
                    ft.Container(self.status_dropdown, expand=1)
                ], spacing=10),
                self.atendente_dropdown,
            ], tight=True, width=500, spacing=20),
            actions=[
                ft.TextButton("CANCELAR", on_click=lambda _: self.page.close(modal)),
                ft.ElevatedButton(
                    "ENVIAR CHAMADO", 
                    bgcolor=ThemeColors.SECONDARY, 
                    color="white",
                    on_click=lambda _: self.handle_submit(modal)
                )
            ]
        )
        self.page.open(modal)

    def handle_submit(self, modal):
        success, message = self.vm.submit_ticket(
            self.comentario_input.value,
            self.categoria_dropdown.value,
            self.status_dropdown.value,
            self.atendente_dropdown.value
        )
        
        if success:
            self.page.close(modal)
            # CORREÇÃO DO SNACKBAR (Nova API do Flet)
            snack = ft.SnackBar(ft.Text(message), bgcolor="green")
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
        else:
            self.comentario_input.error_text = message
            self.page.update()