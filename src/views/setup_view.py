import flet as ft 
from flet import Icons as icons

from themes.themes import Theme 
from controllers.controller import (
    UserDataController,
    DatabaseController
)

import logging


class Setup:
    def __init__(self, theme: Theme, page: ft.Page):
        self.page = page
        self.theme = theme
        self.page.client_storage.clear()
        logging.info("Setting initial values")
        db_instance = DatabaseController()
        db_instance.init_seed()
        logging.info("Setting up mode in out in False")
        self.page.client_storage.set("christianymoon.finance.in_out_mode_setting", False)
        logging.info("Setting up portfolio mode in False")
        self.page.client_storage.set("christianymoon.finance.portfolio_mode", False)
        

    def save_userdata(self, e):
        name = self.setup.controls[2].value
        gender = self.setup.controls[3].value
        if not name:
            return Dialogs.lost_data_dialog(self.page)
        UserDataController.controller_set_userdata(name, gender)
        self.page.go("/")

    def draw(self, header):
        self.setup = ft.Column([
            ft.Text("Configuración Inicial", color=self.theme.text_primary,
                    size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Parece que es la primera vez que usas la aplicación. Por favor ingresa tu nombre y género para continuar.",
                    color=self.theme.text_secondary, size=14),
            ft.TextField(
                hint_text="Nombre",
                hint_style=ft.TextStyle(color=self.theme.text_secondary),
                text_style=ft.TextStyle(color=self.theme.text_primary),
                border=ft.InputBorder.NONE,
                prefix_icon=icons.PERSON,
                bgcolor=self.theme.fg,
                filled=True,
            ),
            ft.Dropdown(
                hint_text="Género",
                options=[
                    ft.dropdown.Option("Masculino"),
                    ft.dropdown.Option("Femenino"),
                ],
                text_style=ft.TextStyle(color=self.theme.text_primary),
                bgcolor=self.theme.fg,
                filled=True,
                border=ft.InputBorder.NONE,
            ),
            ft.ElevatedButton("Guardar", bgcolor=self.theme.green_color,
                              color="#000000", on_click=self.save_userdata)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
        return self.setup
