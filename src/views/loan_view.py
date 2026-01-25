from controller import (
    LoanController,
    ActiveController
)
from flet import Icons as icons
import flet as ft

class LoanView:
    def __init__(self, page: ft.Page, theme):
        self.page = page
        self.theme = theme
        self.data = self.page.data
        self.current_loan = None
        self.accounts = []

    def fetch_loan(self):
        self.current_loan = LoanController.fetch(self.data["loan_id"])
    
    def fetch_accounts(self):
        self.accounts = ActiveController.controller_fetch_actives()

    def liquidate(self, e):
        if not self.account_dropdown.value:
            return

        account_id = self.account_dropdown.value
        LoanController.liquidate(self.data["loan_id"], account_id)
        self.page.go("/")

    def draw(self, header):
        self.fetch_loan()
        self.fetch_accounts()

        if self.current_loan[6]: # If paid
            trend_icon = icons.CHECK_CIRCLE
            trend_color = self.theme.green_color
        else:
            trend_icon = icons.INFO
            trend_color = self.theme.red_color

        self.account_dropdown = ft.Dropdown(
            hint_text="Cuenta origen",
            options=[ft.dropdown.Option(text=f"{account[2]} $ {account[3]}", key=account[0]) for account in self.accounts if account[4]], 
            text_style=ft.TextStyle(color=self.theme.green_color),
            bgcolor=self.theme.fg,
            filled=True,
            border=ft.InputBorder.NONE,
        )

        self.loan_container = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(icons.CREDIT_CARD, # Changed to Credit Card for Loan
                                            color=self.theme.text_primary, size=24),
                            width=40,
                            height=40,
                            bgcolor=self.theme.fg,
                            border_radius=20,
                            alignment=ft.alignment.center
                        ),
                        ft.Column([
                            ft.Text(self.current_loan[1], color=self.theme.text_primary,
                                    size=14, weight=ft.FontWeight.W_500),
                            ft.Text(
                                # Assuming index 7 is created_at/date
                                self.current_loan[7], color=self.theme.text_secondary, size=12),
                        ], spacing=2, expand=True),
                        ft.Container(
                            content=ft.Icon(
                                trend_icon, color=trend_color, size=20),
                            width=30,
                            height=20
                        ),
                        ft.Column([
                            ft.Text(
                                f"${self.current_loan[2]}", color=self.theme.text_primary, size=14, weight=ft.FontWeight.W_500),
                             ft.Text(f"{self.current_loan[3]}%",
                                    color=trend_color, size=12)
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=20, vertical=15),
                    bgcolor=self.theme.fg,
                    border_radius=30,
                    margin=ft.margin.symmetric(horizontal=20, vertical=5),
                ),
                ft.Container(
                     content=ft.Column([
                        self.account_dropdown,
                        ft.Container(
                            content=ft.Text("Liquidar Deuda", color="#000000", size=16, weight=ft.FontWeight.BOLD),
                            bgcolor=self.theme.green_color,
                            padding=15,
                            border_radius=10,
                            alignment=ft.alignment.center,
                            on_click=self.liquidate
                        )
                     ], spacing=20),
                     padding=20
                )
            ]),
            bgcolor=self.theme.bg,
            # padding=10, # Removed outer padding to match style better or keep it if needed 
            # border_radius=10,
        )    

        return ft.Column([
            header.create(placeholder="Prestamos", return_page=True, config=True),
            self.loan_container,
        ])