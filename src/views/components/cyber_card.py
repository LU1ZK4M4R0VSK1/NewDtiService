import flet as ft
from ...utils.constants import ThemeColors

def CyberCard(content, border_color=ThemeColors.PRIMARY):
    return ft.Container(
        content=content,
        border=ft.border.all(1, border_color),
        border_radius=5,
        padding=15,
        bgcolor=ft.Colors.with_opacity(0.05, ThemeColors.PRIMARY),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.1, border_color),
        )
    )