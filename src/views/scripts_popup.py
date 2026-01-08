import flet as ft
from src.utils.constants import ThemeColors

class ScriptsPopups:
    def __init__(self, page: ft.Page, vm, on_refresh):
        self.page = page
        self.vm = vm  # ScriptsViewModel
        self.on_refresh = on_refresh
        
        self.file_picker = ft.FilePicker(on_result=self.on_file_result)
        self.page.overlay.append(self.file_picker)
        
        # Estilo aprimorado para evitar sobreposições
        self.field_style = {
            "border_color": ThemeColors.PRIMARY,
            "focused_border_color": ThemeColors.PRIMARY,
            "label_style": ft.TextStyle(color=ThemeColors.PRIMARY),
            "text_style": ft.TextStyle(color="white"),
            "border_radius": 8,
            "border": ft.InputBorder.OUTLINE, # Força a borda externa
            "content_padding": ft.padding.all(15), # Espaçamento interno para o texto não bater na label
            "bgcolor": "#1A1A1A", # Cor sólida evita transparências problemáticas
        }

        self.name_input = ft.TextField(label="Nome do Script", **self.field_style)
        self.path_input = ft.TextField(label="Caminho", expand=True, **self.field_style)
        self.desc_input = ft.TextField(label="Descrição", multiline=True, min_lines=3, **self.field_style)
        
        # Dropdown com correção de sobreposição
        self.cat_input = ft.Dropdown(
            label="Categoria",
            **self.field_style,
            alignment=ft.alignment.center_left,
            # Força as opções a terem um estilo limpo
            text_size=14,
            options=[
                ft.dropdown.Option("Procedimentos"),
                ft.dropdown.Option("Otimizações")
            ],
        )

    def on_file_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.path_input.value = e.files[0].path
            self.path_input.update()

    def open_form(self, script=None):
        is_edit = script is not None
        self.name_input.value = script.name if is_edit else ""
        self.path_input.value = script.path if is_edit else ""
        self.desc_input.value = script.description if is_edit else ""
        self.cat_input.value = script.category if is_edit else "Procedimentos"

        modal = ft.AlertDialog(
            title=ft.Text(
                "EDITAR SCRIPT" if is_edit else "NOVO SCRIPT", 
                color=ThemeColors.PRIMARY, 
                weight="bold",
                size=20
            ),
            bgcolor="#111111",
            content=ft.Container(
                content=ft.Column([
                    self.name_input,
                    self.cat_input,
                    ft.Row([
                        self.path_input, 
                        ft.IconButton(
                            ft.Icons.FOLDER_OPEN, 
                            icon_color=ThemeColors.PRIMARY,
                            tooltip="Selecionar arquivo",
                            on_click=lambda _: self.file_picker.pick_files()
                        )
                    ], spacing=10),
                    self.desc_input
                ], tight=True, spacing=20),
                width=450,
                padding=ft.padding.symmetric(vertical=10)
            ),
            actions=[
                ft.TextButton("CANCELAR", on_click=lambda _: self.page.close(modal)),
                ft.ElevatedButton(
                    "SALVAR", 
                    bgcolor=ThemeColors.PRIMARY, 
                    color="black",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=lambda _: self.save_action(modal, script.id if is_edit else None)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.open(modal)

    # ... (save_action, confirm_delete e delete_action permanecem iguais)
    def save_action(self, modal, script_id=None):
        if self.name_input.value and self.path_input.value:
            if script_id:
                self.vm.db.execute_query(
                    "UPDATE scripts SET name=?, category=?, path=?, description=? WHERE id=?",
                    (self.name_input.value, self.cat_input.value, self.path_input.value, self.desc_input.value, script_id)
                )
            else:
                self.vm.add_script(self.name_input.value, self.cat_input.value, self.path_input.value, self.desc_input.value)
            
            self.page.close(modal)
            self.on_refresh()

    def confirm_delete(self, script):
        modal = ft.AlertDialog(
            title=ft.Text("EXCLUIR SCRIPT", color=ft.Colors.ERROR, weight="bold"),
            content=ft.Text(f"Deseja apagar '{script.name}'?"),
            actions=[
                ft.TextButton("CANCELAR", on_click=lambda _: self.page.close(modal)),
                ft.ElevatedButton("EXCLUIR", bgcolor=ft.Colors.ERROR, on_click=lambda _: self.delete_action(script.id, modal))
            ]
        )
        self.page.open(modal)

    def delete_action(self, script_id, modal):
        self.vm.db.execute_query("DELETE FROM scripts WHERE id=?", (script_id,))
        self.page.close(modal)
        self.on_refresh()