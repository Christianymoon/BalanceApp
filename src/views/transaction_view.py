from controllers.controller import (
    TransactionController,
    ActiveController,
)

from components.dialogs import Dialogs

from themes.themes import Theme
from flet import Icons as icons
import flet as ft


class TransactionSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.add_transaction = None
        

    def parse_transaction_data(self):
        return {
            "name": self.add_transaction.content.controls[0].value,
            "category": self.add_transaction.content.controls[1].value,
            "price": self.add_transaction.content.controls[2].value,
            "type": self.radiogroup_ref.current.value,
            "account_id": self.add_transaction.content.controls[4].value,
        }

    def add_transaction_database(self, e):
        transaction_data = self.parse_transaction_data()
        if transaction_data["type"] == "credit":
            transaction_data["account_id"] = "Credito"
        if transaction_data["price"] == "" or transaction_data["name"] == "" or transaction_data["category"] == "" or transaction_data["account_id"] is None:
            return Dialogs.lost_data_dialog(self.page)
        try:
            TransactionController.controller_set_transaction(transaction_data)
            self.page.go("/")
        except Exception as e:
            Dialogs.error_dialog(self.page, str(e))

    def radio_group_event(self, e):
        if e.control.value == "credit":
            self.add_transaction.content.controls[4].disabled = True
        else:
            self.add_transaction.content.controls[4].disabled = False
        self.page.update()

    def draw(self, header):
        self.accounts_actives = ActiveController.controller_fetch_actives()
        self.radiogroup_ref = ft.Ref[ft.RadioGroup]()
        self.add_transaction = ft.Container(
            bgcolor=self.theme.bg,
            padding=10,
            content=ft.Column([
            #Name 0
            ft.TextField(
                hint_text="Nombre",
                hint_style=ft.TextStyle(color=self.theme.text_secondary),
                text_style=ft.TextStyle(color=self.theme.text_primary),
                border=ft.InputBorder.NONE,
                prefix_icon=icons.PERSON,
                bgcolor=self.theme.fg,
                filled=True,
            ),
            #Category 1
            ft.TextField(
                hint_text="Categoria",
                hint_style=ft.TextStyle(color=self.theme.text_secondary),
                text_style=ft.TextStyle(color=self.theme.text_primary),
                border=ft.InputBorder.NONE,
                prefix_icon=icons.FILTER,
                bgcolor=self.theme.fg,
                filled=True,
            ),
            #Mount 2
            ft.TextField(
                hint_text="Monto",
                hint_style=ft.TextStyle(color=self.theme.text_secondary),
                text_style=ft.TextStyle(color=self.theme.text_primary),
                border=ft.InputBorder.NONE,
                prefix_icon=icons.ATTACH_MONEY,
                bgcolor=self.theme.fg,
                filled=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                input_filter=ft.InputFilter(
                allow=True, regex_string=r"^\d*\.?\d*$"),
            ),
            #Type 3
            ft.RadioGroup(
                ref=self.radiogroup_ref,
                value="spent",
                content=ft.Row([
                    ft.Radio(value="spent", label="Gasto"),
                    ft.Radio(value="income", label="Ingreso"),
                    ft.Radio(value="credit", label="Credito")
                ]),
                on_change=self.radio_group_event,
            ),  
            #Account 4
            ft.Dropdown(
                hint_text="Cuenta origen",
                options=[ft.dropdown.Option(text=f"{account[2]} ${account[3]}", key=account[0]) for account in self.accounts_actives if account[4]],
                text_style=ft.TextStyle(color=self.theme.green_color),
                bgcolor=self.theme.fg,
                filled=True,
                border=ft.InputBorder.NONE,
            ),
            #Button 5
            ft.Row([
                ft.IconButton(
                icon=icons.DOUBLE_ARROW,
                icon_color=self.theme.text_primary,
                on_click=self.add_transaction_database,
                icon_size=24
                ),
                ft.Text("Transaccionar", color=self.theme.text_primary,
                    size=14, weight=ft.FontWeight.W_500)
            ]),
            ], expand=True)
        )
        return ft.Column([
            header.create("Transacciones", return_page=True),
            self.add_transaction,
        ], expand=True, spacing=0, scroll=ft.ScrollMode.AUTO)

