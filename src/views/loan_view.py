from controllers.controller import (
    LoanController,
    ActiveController
)

from components.dialogs import Dialogs
from flet import Icons as icons
import flet as ft
from themes.themes import Theme

class LoanView:
    def __init__(self, theme: Theme, page: ft.Page):
        self.page = page
        self.theme = theme
        self.data = self.page.data
        self.current_loan = None
        self.accounts = []

    def fetch_loan(self):
        self.current_loan = LoanController.fetch(self.data["loan_id"])
    
    def fetch_accounts(self):
        self.accounts = ActiveController.controller_fetch_actives()

    def delete(self, e):
        LoanController.delete(self.data["loan_id"])
        self.page.go("/borrows")

    def liquidate(self, e):
        if not self.account_dropdown.value:
            Dialogs.error_dialog(self.page, "Selecciona una cuenta")
            return
        
        account_id = self.account_dropdown.value

        try:
            LoanController.liquidate(self.data["loan_id"], self.current_loan[1], account_id)
            self.page.go("/")
        except Exception as e:
            Dialogs.error_dialog(self.page, str(e))
        
        self.page.update()

    def draw(self, header):
        self.fetch_loan()
        self.fetch_accounts()

        self.header = header.create(placeholder="Prestamos", return_page=True, config=True)

        self.card = ft.Container(
            ft.Column([
                ft.Text(self.current_loan[2].capitalize(), size=16, weight=ft.FontWeight.W_500),

                ft.Divider(),

                ft.Row(
                    [
                        ft.Text("Interes: "),
                        ft.Text(str(self.current_loan[4]) + "%")
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=10
                ),

                ft.Row(
                    [
                        ft.Text("Fecha: "),
                        ft.Text(self.current_loan[8])
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=10
                ),
                

                ft.Row(
                    [
                        ft.Text("Deuda: "),
                        ft.Text("$" + str(self.current_loan[3]))
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=10
                ),


                ft.Row(
                    [
                        ft.Icon(icons.CHECK_CIRCLE if self.current_loan[7] else icons.CANCEL, color=self.theme.green_color if self.current_loan[7] else self.theme.red_color, size=20), 
                        ft.Text("Cobrado" if self.current_loan[7] else "Aun sin cobrar", size=14)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=10
                ),
                
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=10),
            padding=ft.padding.symmetric(horizontal=10, vertical=15),
            border_radius=20,
            bgcolor=self.theme.fg,
        )

        self.account_dropdown = ft.Dropdown(
            hint_text="Cuenta origen",
            options=[ft.dropdown.Option(text=f"{account[2]} $ {account[3]}", key=account[0]) for account in self.accounts if account[4]], 
            text_style=ft.TextStyle(color=self.theme.green_color),
            bgcolor=self.theme.bg,
            filled=True,
            border=ft.InputBorder.OUTLINE,
            border_radius=20,
            visible=not self.current_loan[7],
        )

        self.hint_text = ft.Text("Al cobrar el prestamo se sumara la cantidad a la cuenta seleccionada", color=self.theme.text_secondary, size=12)

        self.space = ft.Container(ft.Column(), expand=True)

        self.delete_button = ft.Container(
            content=ft.Text("Eliminar", color=self.theme.bg, size=16, weight=ft.FontWeight.BOLD),
            bgcolor=self.theme.red_color,
            padding=15,
            border_radius=20,
            alignment=ft.alignment.center,
            on_click=self.delete,
            visible=self.current_loan[7] == True,
        )

        self.liquidate_button = ft.Container(
            content=ft.Text("Liquidar prestamo", color=self.theme.bg, size=16, weight=ft.FontWeight.BOLD),
            bgcolor=self.theme.green_color,
            padding=15,
            border_radius=20,
            alignment=ft.alignment.center,
            on_click=self.liquidate,
            visible=not self.current_loan[7],
        )

        return ft.Container(
            ft.Column([
                self.header,
                self.card,
                self.account_dropdown,
                self.hint_text,
                self.space,
                self.liquidate_button,
                self.delete_button,
            ]),
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
            expand=True
        )