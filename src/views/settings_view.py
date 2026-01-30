from controllers.controller import (
    DatabaseController,
)

from themes.themes import Theme
from flet import Icons as icons
import flet as ft
import os
import shutil
import logging

from setup import log_dir


class Settings:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.in_out_mode_value = self.page.client_storage.get("christianymoon.finance.in_out_mode_setting")

    def handle_reset_database(self, e):
        db_instance = DatabaseController()
        db_instance.drop_tables()
        db_instance.create_tables()
        db_instance.init_seed()
        self.page.go("/")

    def handle_in_out_mode(self, e):
        try:
            value = self.page.client_storage.get("christianymoon.finance.in_out_mode_setting")
            self.page.client_storage.remove("christianymoon.finance.in_out_mode_setting")
            self.page.client_storage.set("christianymoon.finance.in_out_mode_setting", not value)
            self.in_out_mode_value = not value
        except:
            logging.error(f"Error during change in out mode, {e}", exc_info=True)

        self.page.update()

    def draw(self, header):

        self.header = header.create("Configuracion", return_page=True)

        self.in_out_mode_switch = ft.Row(
            [
                ft.Text("Modo solo transacciones"),
                ft.CupertinoSwitch(
                    value=self.in_out_mode_value,
                    scale=0.6,
                    key="in_out_mode",
                    on_change=self.handle_in_out_mode,
                ),
                
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN 
        )

        self.space = ft.Container(ft.Column(), expand=True)

        self.reset_button = ft.Container(
            content=ft.Text("Reestablecer Base de Datos", color=self.theme.bg, size=16, weight=ft.FontWeight.BOLD),
            bgcolor=self.theme.red_color,
            padding=15,
            border_radius=20,
            alignment=ft.alignment.center,
            on_click=self.handle_reset_database,
        )

        return ft.Container(
            ft.Column([
                self.header,
                self.in_out_mode_switch,
                self.space,
                self.reset_button
            ]),
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
            expand=True,
        )