import flet as ft
import sys
import os

# Detecta se está rodando como .exe (PyInstaller) ou em desenvolvimento
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    BASE_DIR = BASE_DIR

def get_theme():
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ThemeColors.PRIMARY,
            secondary=ThemeColors.SECONDARY,
            surface=ThemeColors.SURFACE,
            surface_container=ThemeColors.SURFACE,
            surface_container_low=ThemeColors.SURFACE,
            surface_container_high=ThemeColors.SURFACE,
            surface_container_highest=ThemeColors.SURFACE,
            surface_container_lowest=ThemeColors.SURFACE,
            surface_dim=ThemeColors.SURFACE,
            surface_bright=ThemeColors.SURFACE,
            error=ThemeColors.ERROR,
            on_surface=ThemeColors.TEXT,
            on_primary=ThemeColors.TEXT,
            outline=ThemeColors.DISABLED,
        ),
        font_family=AppConfig.FONT_FAMILY,
        visual_density=ft.VisualDensity.COMFORTABLE, 
    )