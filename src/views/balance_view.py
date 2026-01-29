from controllers.controller import (
    BalanceController,
)

from themes.themes import Theme
from flet import Icons as icons
import flet as ft


class BalanceSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.balance_content = None

    def add_balance_database(self, e):
        new_balance = self.balance_content.controls[1].controls[3].value
        if new_balance == "":
            return Dialogs.lost_data_dialog(self.page)
        BalanceController.controller_set_balance(float(new_balance), new=True)

    def draw(self, header):
        self.balance_content = ft.Column([
            header.create("Balance", return_page=True),
            ft.Column([
                ft.Text("Balance Actual",
                        color=self.theme.text_secondary, size=24),
                ft.Text(f"{BalanceController.controller_fetch_balance(formated=True)}",
                        color=self.theme.text_primary, size=32, weight=ft.FontWeight.BOLD),
                ft.Text(
                    f"Ultima actualizacion: {BalanceController.fetch_balance_update()}", color=self.theme.text_secondary, size=14),
                ft.TextField(
                    hint_text="Nuevo Balance",
                    hint_style=ft.TextStyle(color=self.theme.text_secondary),
                    text_style=ft.TextStyle(color=self.theme.text_primary),
                    border=ft.InputBorder.NONE,
                    bgcolor=self.theme.fg,
                    filled=True,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    input_filter=ft.InputFilter(
                        allow=True, regex_string=r"^\d*\.?\d*$"),
                ),
                ft.ElevatedButton("Actualizar Balance", bgcolor=self.theme.green_color,
                                  color="#000000", on_click=self.add_balance_database)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        return self.balance_content

