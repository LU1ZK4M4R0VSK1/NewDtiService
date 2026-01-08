import flet as ft

class ThemeColors:
    PRIMARY = "#00FF00"      # Verde Neon
    SECONDARY = "#00CC00"    # Verde Escuro
    BACKGROUND = "#0A0A0A"   # Preto Absoluto
    SURFACE = "#1A1A1A"      # Cinza Escuro
    ERROR = "#FF0033"        # Vermelho Neon
    TEXT = "#FFFFFF"         # Branco
    DISABLED = "#666666"     # Cinza

class AppConfig:
    DB_NAME = "library.db"
    FONT_FAMILY = "Consolas, monospace" # Estilo Terminal/Hacker

def get_theme():
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ThemeColors.PRIMARY,
            secondary=ThemeColors.SECONDARY,
            background=ThemeColors.BACKGROUND,
            surface=ThemeColors.SURFACE,
            error=ThemeColors.ERROR,
            on_background=ThemeColors.TEXT,
            on_surface=ThemeColors.TEXT,
        ),
        font_family=AppConfig.FONT_FAMILY,
        # Alterado de ft.ThemeVisualDensity para ft.VisualDensity
        visual_density=ft.VisualDensity.COMFORTABLE, 
    )