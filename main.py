import flet as ft
from src.utils.constants import get_theme, ThemeColors
from src.views.system_sidebar import SystemSidebar
from src.views.scripts_tab import ScriptsTab
from src.views.printers_tab import PrintersTab

def main(page: ft.Page):
    page.title = "DTI Service v3.0"
    page.theme = get_theme()
    page.theme_mode = ft.ThemeMode.DARK
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
        padding=ft.padding.only(left=20, right=20, top=10, bottom=10),
        bgcolor=ThemeColors.SURFACE,
        border=ft.border.only(bottom=ft.BorderSide(1, ThemeColors.SURFACE)),
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
    
    tabs = ft.Tabs(
        selected_index=0,
        indicator_color=ThemeColors.PRIMARY,
        label_color=ThemeColors.PRIMARY,
        unselected_label_color=ThemeColors.DISABLED,
        on_change=lambda _: refresh_all_tabs(), # Atualiza ao trocar de aba
        tabs=[
            ft.Tab(text="PROCEDIMENTOS", icon=ft.Icons.CODE, content=scripts_content),
            ft.Tab(text="IMPRESSORAS", icon=ft.Icons.PRINT, content=printers_content),
            ft.Tab(text="OTIMIZAÇÕES", icon=ft.Icons.ROCKET_LAUNCH, content=optimizations_content),
        ],
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
    ft.app(target=main, assets_dir="src/assets")