from controllers.controller import (
    ActiveController,
)

from components.dialogs import Dialogs

from themes.themes import Theme 
from flet import Icons as icons 
import flet as ft


class ActiveSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.checkboxes = False
        self.active_list = None
        self.active_section = None
        self.selected_actives = []

    def add_active_database(self, e):
        active_type = self.dropdown.value
        name = self.name_field.value
        amount = self.value_field.value
        is_liquid = self.liquid_checkbox.value
        if amount == "" or name == "" or active_type is None:
            return Dialogs.lost_data_dialog(self.page)

        ActiveController.controller_set_active(
            name, active_type, amount, is_liquid)
        self.refresh_actives()

    def parse_selected_actives(self, e):
        ide = e.control.data
        if ide in self.selected_actives:
            self.selected_actives.remove(ide)
        else:
            self.selected_actives.append(ide)

    def delete_active(self, e):
        if len(self.selected_actives) > 0:
            for active_id in self.selected_actives:
                ActiveController.controller_delete_active(active_id)
            self.selected_actives.clear()
            self.refresh_actives()

    def show_checkboxes(self, e=None):
        self.checkboxes = not self.checkboxes
        self.refresh_actives()

    def add_active_list(self, actives_list):
        self.active_list.controls.clear()
        for item in reversed(actives_list):
            self.active_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Checkbox(
                            value=item[4], on_change=self.parse_selected_actives, data=item[0], visible=self.checkboxes),
                        ft.Container(
                            content=ft.Icon(icons.TRENDING_UP,
                                            color=self.theme.green_color, size=24),
                            width=40,
                            height=40,
                            bgcolor=self.theme.bg,
                            border_radius=20,
                            alignment=ft.alignment.center
                        ),
                        ft.Column([
                            ft.Text(item[2], color=self.theme.text_primary,
                                    size=14, weight=ft.FontWeight.W_500),
                            ft.Text(
                                item[1], color=self.theme.text_secondary, size=12)
                        ], spacing=2, expand=True),
                        ft.Container(
                            content=ft.Icon(
                                icons.CHECK_CIRCLE if item[4] else icons.ERROR, color=self.theme.green_color if item[4] else self.theme.red_color, size=20),
                            width=30,
                            height=20
                        ),
                        ft.Column([
                            ft.Text(
                                f"${item[3]:.2f}", color=self.theme.text_primary, size=14, weight=ft.FontWeight.W_500),
                            ft.Text(
                                "Liquido" if item[4] else "No Liquido", color=self.theme.green_color if item[4] else self.theme.red_color, size=12)
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    margin=ft.margin.symmetric(vertical=5),
                    padding=ft.padding.symmetric(horizontal=10, vertical=15),
                    border_radius=20,
                    bgcolor=self.theme.fg
                )
            )
        self.page.update()

    def refresh_actives(self, *args):
        self.active_list.controls.clear()
        self.add_active_list(ActiveController.controller_fetch_actives())
        self.page.update()

    def draw(self, header):
        
        self.header = header.create("Activos", return_page=True)

        self.hint_text = ft.Text("Selecciona tipo de activo", color=self.theme.text_primary,
                    size=14, weight=ft.FontWeight.W_500)

        self.dropdown = ft.Dropdown(
                hint_text="Tipo de activo",
                options=[
                    ft.dropdown.Option("Acciones"),
                    ft.dropdown.Option("Bonos"),
                    ft.dropdown.Option("Fondos"),
                    ft.dropdown.Option("Criptomonedas"),
                    ft.dropdown.Option("Bienes raíces"),
                    ft.dropdown.Option("Venta"),
                    ft.dropdown.Option("Otros"),
                ],
                text_style=ft.TextStyle(color=self.theme.text_primary),
                bgcolor=self.theme.fg,
                filled=True,
                border=ft.InputBorder.OUTLINE,
                border_radius=20,
            )

        self.name_field = ft.TextField(
                hint_text="Nombre del activo",
                hint_style=ft.TextStyle(color=self.theme.text_secondary),
                text_style=ft.TextStyle(color=self.theme.text_primary),
                border=ft.InputBorder.OUTLINE,
                prefix_icon=icons.PERSON,
                bgcolor=self.theme.fg,
                filled=True,
                border_radius=20,
            )

        self.value_field = ft.TextField(
                hint_text="Valor del activo",
                hint_style=ft.TextStyle(color=self.theme.text_secondary),
                text_style=ft.TextStyle(color=self.theme.text_primary),
                border=ft.InputBorder.OUTLINE,
                prefix_icon=icons.ATTACH_MONEY,
                bgcolor=self.theme.fg,
                filled=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                input_filter=ft.InputFilter(
                    allow=True, regex_string=r"^\d*\.?\d*$"),
                border_radius=20,
            )

        self.liquid_checkbox = ft.Checkbox(label="Es liquido", value=False)

        self.panel = ft.Row([
                ft.IconButton(
                    icon=icons.TRENDING_UP, icon_color=self.theme.text_primary,
                    on_click=self.add_active_database, icon_size=24
                ),
                ft.IconButton(
                    icon=icons.DELETE,
                    icon_color=self.theme.text_primary,
                    tooltip="Eliminar Pasivo(s)",
                    on_click=self.delete_active,
                    icon_size=24,
                ),
                ft.IconButton(
                    icon=icons.REFRESH,
                    icon_color=self.theme.text_primary,
                    tooltip="Refrescar Lista",
                    on_click=self.refresh_actives,
                    icon_size=24,
                ),
                ft.IconButton(
                    icon=icons.FILTER_LIST,
                    icon_color=self.theme.text_primary,
                    tooltip="Seleccionar",
                    on_click=self.show_checkboxes,
                    icon_size=24,
                ),
                ft.IconButton(
                    icon=icons.SYNC_ALT,
                    icon_color=self.theme.text_primary,
                    tooltip="Intertransferencia",
                    on_click=lambda e: self.page.go("/intertransfer"),
                    icon_size=24,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.active_list = ft.Column(
            [], spacing=0, scroll=ft.ScrollMode.ADAPTIVE, expand=True)

        self.add_active_list(ActiveController.controller_fetch_actives())

        self.active_section = ft.Container(
            ft.Column([
                self.header,
                self.hint_text,
                self.dropdown,
                self.name_field,
                self.value_field,
                self.liquid_checkbox,
                self.panel,
                self.active_list,
            ],),
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
            expand=True,
        )
        
        return self.active_section







