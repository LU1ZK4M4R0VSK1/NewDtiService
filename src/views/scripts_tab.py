import flet as ft
from src.viewmodels.scripts_vm import ScriptsViewModel
from src.utils.constants import ThemeColors
from src.views.components.cyber_card import CyberCard
from src.views.scripts_popup import ScriptsPopups 
from src.views.tickets_popup import TicketsPopup

class ScriptsTab(ft.Container):
    def __init__(self, category_filter="Procedimentos"):
        super().__init__(expand=True, padding=20)
        self.vm = ScriptsViewModel()
        self.category_filter = category_filter
        self.list_view = ft.ListView(expand=True, spacing=10)
        
        # Inicializar popups como None para agora
        self.popups = None
        self.ticket_popup = None

        # Título dinâmico baseado na categoria
        display_title = "AUTOMAÇÃO & SCRIPTS" if self.category_filter == "Procedimentos" else "OTIMIZAÇÕES DE SISTEMA"

        self.content = ft.Column([
            ft.Row([
                ft.Text(display_title, size=24, weight="bold", color=ThemeColors.PRIMARY),
                ft.IconButton(ft.Icons.REFRESH, on_click=lambda _: self.refresh_scripts())
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.list_view
        ], expand=True)
        
        self.refresh_scripts(initial=True)

    def did_mount(self):
        # Passamos uma função lambda para o refresh para garantir que atualize a instância correta
        self.popups = ScriptsPopups(self.page, self.vm, lambda: self.refresh_scripts())
        self.ticket_popup = TicketsPopup(self.page)

    def refresh_scripts(self, initial=False):
        # Busca todos os scripts do banco
        all_scripts = self.vm.load_scripts()
        
        # Filtra apenas os scripts que pertencem a esta aba específica
        scripts = [s for s in all_scripts if s.category == self.category_filter]
        
        self.list_view.controls = [self.build_script_item(s) for s in scripts]
        if not initial:
            self.update()

    def open_add_modal(self, e):
        if self.popups:
            self.popups.open_form()

    def open_ticket_modal(self, e):
        if self.ticket_popup:
            self.ticket_popup.open()

    def run_click(self, script, output_text):
        output_text.value = f"> Executando {script.name}...\n"
        output_text.color = ThemeColors.TEXT
        self.update()
        self.page.run_thread(lambda: self._run_script_worker(script, output_text))

    def _run_script_worker(self, script, output_text):
        def append_chunk(chunk: str):
            output_text.value += chunk
            self.page.update()

        success, result = self.vm.run_script(script, on_output=append_chunk)

        if not success:
            normalized_result = (result or "").strip()
            current = (output_text.value or "")
            if normalized_result and normalized_result not in current:
                output_text.value += f"\n{normalized_result}\n"

        output_text.color = ThemeColors.PRIMARY if success else ThemeColors.ERROR
        self.page.update()

    def build_script_item(self, script):
        output_view = ft.Text(value="> Pronto.", font_family="Consolas", size=11)
        return CyberCard(
            ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.TERMINAL, color=ThemeColors.PRIMARY, size=20),
                        ft.Text(script.name, weight="bold", size=16),
                    ]),
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.EDIT_OUTLINED,
                            icon_color=ThemeColors.PRIMARY,
                            icon_size=18,
                            on_click=lambda _: self.popups.open_form(script)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINED,
                            icon_color=ThemeColors.ERROR,
                            icon_size=18,
                            on_click=lambda _: self.popups.confirm_delete(script)
                        ),
                    ], spacing=0)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Text(script.description, size=12, italic=True, color=ThemeColors.DISABLED),
                ft.Divider(color=ThemeColors.SURFACE, height=1),
                ft.Container(
                    content=output_view, bgcolor="#0a0a0a", padding=10, border_radius=5, width=float('inf')
                ),
                ft.Row([
                    ft.ElevatedButton(
                        "EXECUTAR", icon=ft.Icons.PLAY_ARROW,
                        style=ft.ButtonStyle(color="black", bgcolor=ThemeColors.PRIMARY),
                        on_click=lambda _: self.run_click(script, output_view)
                    )
                ], alignment=ft.MainAxisAlignment.END)
            ])
        )