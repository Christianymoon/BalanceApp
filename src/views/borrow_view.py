from controllers.controller import (
    LoanController,
    ActiveController,
)

from components.dialogs import Dialogs

from themes.themes import Theme
from flet import Icons as icons
import flet as ft


class BorrowSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page

    def handle_loan(self, e, value):
        self.page.data = {
            "loan_id": value,
            "active_id": None 
        }
        self.page.go("/loan")

    def get_loan_data(self, e):
        loan_name = self.loan_form.controls[0].value
        loan_amount = self.loan_form.controls[1].value
        loan_interest = self.loan_form.controls[2].value
        source_account = self.account_dropdown.value
        loan_to = self.group1_value.current.value
        loan_from = self.group2_value.current.value

        if loan_from == "bank":
            source_account = "bank"

        if loan_name == "" or loan_amount == "" or loan_interest == "" or source_account is None:
            return Dialogs.lost_data_dialog(self.page)

        return {
            "name": loan_name,
            "amount": float(loan_amount),
            "interest": float(loan_interest),
            "source_account": source_account,
            "to": loan_to,
            "from": loan_from,
        }
    
    def set_loan_database(self, e):
        loan_data = self.get_loan_data(e)
        if not loan_data:
            return

        try:
            LoanController.set(
                loan_data["name"],
                loan_data["amount"],
                loan_data["interest"],
                loan_data["source_account"],
                loan_data["to"],
                loan_data["from"],
            )
        except Exception as e:
            Dialogs.error_dialog(self.page, str(e))
            return

        self.page.go("/")

    def draw_loans(self, list_control):
        loans = LoanController.controller_fetch_loans()
        list_control.controls.clear()
        for loan in loans:
            list_control.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(icons.CREDIT_CARD,
                                            color=self.theme.text_primary, size=24),
                            width=40,
                            height=40,
                            bgcolor=self.theme.fg,
                            border_radius=20,
                            alignment=ft.alignment.center
                        ),
                        ft.Column([
                            ft.Text(loan[2], color=self.theme.text_primary,
                                    size=14, weight=ft.FontWeight.W_500),
                            ft.Text(
                                str(loan[8]), color=self.theme.text_secondary, size=12)
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(
                                f"${loan[3]}", color=self.theme.text_primary, size=14, weight=ft.FontWeight.W_500),
                            ft.Text(f"{loan[4]}%",
                                    color=self.theme.text_secondary, size=12),
                            ft.Text(
                                "Pagado" if loan[7] else "Pendiente", color=self.theme.green_color if loan[7] else self.theme.red_color, size=12)
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=10, vertical=15),
                    bgcolor=self.theme.fg,
                    border_radius=20,
                    on_click=lambda e: self.handle_loan(e, loan[0])
                )
            )
        self.page.update()
        

    def ui_events(self, e):
        if e.control.value == "bank":
            self.account_dropdown.disabled = True
        else:
            self.account_dropdown.disabled = False
        self.page.update()

    def draw(self, header):

        self.accounts_actives = ActiveController.controller_fetch_actives()

        self.header = header.create("Préstamos", return_page=True)

        self.group1_value = ft.Ref[ft.RadioGroup]()

        self.group2_value = ft.Ref[ft.RadioGroup]()

        self.loan_to = ft.Row([
            ft.RadioGroup(
                ref=self.group1_value,
                value="terciary",
                content=ft.Row([
                    ft.Radio(value="terciary", label="Terceros"),
                ]),
            ),
        ])

        self.loan_from = ft.Row([
            ft.RadioGroup(
                ref=self.group2_value,
                value="liquidity",
                content=ft.Row([
                    ft.Radio(value="liquidity", label="Liquidez"),
                    ft.Radio(value="bank", label="Crédito"),
                ]),
                on_change=self.ui_events,
            ),
        ])

        self.options = ft.Container(
            ft.Column([
                ft.Text("Prestamo a:", color=self.theme.text_primary,),
                self.loan_to,
                ft.Text("Desde:", color=self.theme.text_primary,),
                self.loan_from,
            ]),
        )
           
        self.loan_form = ft.Column([
            ft.TextField(
            hint_text="Nombre del préstamo",
            border=ft.InputBorder.OUTLINE,
            hint_style=ft.TextStyle(color=self.theme.text_secondary),
            text_style=ft.TextStyle(color=self.theme.text_primary),
            prefix_icon=icons.PERSON,
            bgcolor=self.theme.fg,
            filled=True,
            border_radius=20,
            ),
            ft.TextField(
            hint_text="Monto del préstamo",
            hint_style=ft.TextStyle(color=self.theme.text_secondary),
            text_style=ft.TextStyle(color=self.theme.text_primary),
            border=ft.InputBorder.OUTLINE,
            prefix_icon=icons.ATTACH_MONEY,
            bgcolor=self.theme.fg,
            filled=True,
            border_radius=20,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$"),
            ),
            ft.TextField(
            hint_text="Porcentaje de interés (%)",
            value=0,
            hint_style=ft.TextStyle(color=self.theme.text_secondary),
            text_style=ft.TextStyle(color=self.theme.text_primary),
            border=ft.InputBorder.OUTLINE,
            prefix_icon=icons.PERCENT,
            bgcolor=self.theme.fg,
            filled=True,
            border_radius=20,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$"),
            ),
        ])

        self.account_dropdown = ft.Dropdown(
            hint_text="Cuenta origen",
            options=[ft.dropdown.Option(text=f"{account[2]} ${account[3]}", key=account[0]) for account in self.accounts_actives if account[4]],
            text_style=ft.TextStyle(color=self.theme.green_color),
            bgcolor=self.theme.fg,
            filled=True,
            border=ft.InputBorder.OUTLINE,
            border_radius=20,
        )

        self.add_button = ft.Container(
            content=ft.Text("Agregar", color=self.theme.bg, size=16, weight=ft.FontWeight.BOLD),
            bgcolor=self.theme.green_color,
            padding=15,
            border_radius=20,
            alignment=ft.alignment.center,
            on_click=self.set_loan_database,
        )

        self.loan_list = ft.Column([])

        self.draw_loans(self.loan_list)

        return ft.Container(
            ft.Column([
                self.header,
                self.options,
                self.loan_form,
                self.account_dropdown,
                self.add_button,
                self.loan_list,
            ], expand=True, scroll=ft.ScrollMode.ADAPTIVE),
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
            expand=True,
        )

