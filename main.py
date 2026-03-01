import flet as ft
import threading
from src.utils.constants import get_theme, ThemeColors
from src.views.system_sidebar import SystemSidebar
from src.views.scripts_tab import ScriptsTab
from src.views.printers_tab import PrintersTab
from src.services.shortcut_service import shortcut_exists, create_admin_shortcut

def _ensure_shortcut():
    """Cria o atalho na área de trabalho pública se ainda não existir."""
    if not shortcut_exists():
        create_admin_shortcut()

def main(page: ft.Page):
    # Garante o atalho na área de trabalho (em background para não travar a UI)
    threading.Thread(target=_ensure_shortcut, daemon=True).start()

    page.title = "DTI Service v3.0"
    page.theme = get_theme()
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ThemeColors.BACKGROUND
    page.padding = 0
    page.window_min_width = 1100
    page.window_min_height = 700

    # Instanciação dos Componentes
    sidebar = SystemSidebar()
    
    # Criamos duas instâncias da mesma classe, mudando apenas o filtro de categoria
    scripts_content = ScriptsTab(category_filter="Procedimentos")
    optimizations_content = ScriptsTab(category_filter="Otimizações")
    
    printers_content = PrintersTab()

    # Função para atualizar ambas as abas de scripts simultaneamente
    def refresh_all_tabs():
        scripts_content.refresh_scripts()
        optimizations_content.refresh_scripts()

    # Handlers de Eventos
    def on_add_script_click(e):
        # Abre o modal de adição (passando o refresh global para atualizar as duas abas)
        scripts_content.open_add_modal(e)

    def on_open_ticket_click(e):
        scripts_content.open_ticket_modal(e)

    header = ft.Container(
        padding=ft.Padding(left=20, right=20, top=10, bottom=10),
        bgcolor=ThemeColors.SURFACE,
        border=ft.Border(bottom=ft.BorderSide(1, ThemeColors.SURFACE)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("DTI SERVICE", weight="bold", size=22, color=ThemeColors.PRIMARY),
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.TextButton(
                            "ADICIONAR SCRIPT",
                            icon=ft.Icons.ADD_BOX_OUTLINED,
                            style=ft.ButtonStyle(color=ThemeColors.PRIMARY),
                            on_click=on_add_script_click
                        ),
                        ft.TextButton(
                            "ABRIR CHAMADO",
                            icon=ft.Icons.CONFIRMATION_NUMBER_OUTLINED,
                            style=ft.ButtonStyle(color=ThemeColors.SECONDARY),
                            on_click=on_open_ticket_click
                        ),
                    ]
                )
            ]
        )
    )
    
    # Flet 0.80+ Tabs API: use TabBar + TabBarView inside Tabs(content, length)
    tab_items = [
        ft.Tab(label="PROCEDIMENTOS", icon=ft.Icons.CODE),
        ft.Tab(label="IMPRESSORAS", icon=ft.Icons.PRINT),
        ft.Tab(label="OTIMIZAÇÕES", icon=ft.Icons.ROCKET_LAUNCH),
    ]

    tab_bar = ft.TabBar(
        tabs=tab_items,
        indicator_color=ThemeColors.PRIMARY,
        label_color=ThemeColors.PRIMARY,
        unselected_label_color=ThemeColors.DISABLED,
    )

    tab_view = ft.TabBarView(
        controls=[
            scripts_content,
            printers_content,
            optimizations_content,
        ],
        expand=True,
    )

    tabs = ft.Tabs(
        content=ft.Container(
            expand=True,
            content=ft.Column(
                spacing=0,
                expand=True,
                controls=[
                    tab_bar,
                    ft.Container(expand=True, content=tab_view),
                ],
            ),
        ),
        length=len(tab_items),
        selected_index=0,
        on_change=lambda _: refresh_all_tabs(),  # Atualiza ao trocar de aba
        expand=True,
    )

    main_layout = ft.Column(
        spacing=0, 
        expand=True,
        controls=[
            header,
            ft.Row(
                expand=True, 
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH, 
                controls=[
                    sidebar,
                    ft.VerticalDivider(width=1, color=ThemeColors.SURFACE),
                    ft.Container(content=tabs, expand=True, padding=10)
                ],
            )
        ]
    )

    page.add(main_layout)

if __name__ == "__main__":
    ft.run(main=main, assets_dir="src/assets")