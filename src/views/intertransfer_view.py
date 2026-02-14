import flet as ft 
from themes.themes import Theme 
from flet import Icons as icons

from components.headers import HeaderSection
from components.dialogs import Dialogs

from controllers.controller import ActiveController

class IntertransferView:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.accounts = []
        self.temp_account_from = None
        self.temp_account_to = None

    def intertransfer(self, e):
        try:
            ActiveController.controller_intertransfer(self.temp_account_from, self.temp_account_to, self.quantity_field.value)
            self.page.go("/active")
        except Exception as e:
            Dialogs.error_dialog(self.page, str(e))

    def validate_quantity(self, e):
        if e.control.value == "":
            return

        self.total_account = ActiveController.controller_fetch_active(self.temp_account_from)
        if self.total_account[3] < float(e.control.value):
            e.control.error_text = f"La cantidad no puede ser mayor a la de la cuenta {self.total_account[2]}"
            e.control.update()
            self.transfer_button.disabled = True
            self.transfer_button.bgcolor = self.theme.red_color
            self.transfer_button.update()
            return
        e.control.error_text = ""
        e.control.update()
        self.transfer_button.disabled = False
        self.transfer_button.bgcolor = self.theme.green_color
        self.transfer_button.update()

    def validate_accounts(self, e):
        self.quantity_field.value = ""
        self.quantity_field.error_text = ""
        self.quantity_field.update()
        if self.account_from.value == self.account_to.value:
            self.spawn_error.value = "Las cuentas no pueden ser iguales"
            self.spawn_error.update()
            self.quantity_field.disabled = True
            self.quantity_field.update()
            self.transfer_button.disabled = True
            self.transfer_button.bgcolor = self.theme.red_color
            self.transfer_button.update()
            return
        self.spawn_error.value = ""
        self.spawn_error.update()
        self.quantity_field.disabled = False
        self.quantity_field.update()
        self.transfer_button.disabled = False
        self.transfer_button.bgcolor = self.theme.green_color
        self.transfer_button.update()
        self.temp_account_to = self.account_to.value
        self.temp_account_from = self.account_from.value

    def add_intertransactions(self):
        self.intertransactions = ActiveController.controller_fetch_intertransactions()
        for intertransaction in reversed(self.intertransactions):
            self.intertransactions_container.content.controls.append(
                ft.Container(
                    content=ft.ResponsiveRow([

                        ft.Row([
                            ft.Text(f"$ {intertransaction[3]:.2f}", color=self.theme.green_color, size=12),
                            ft.Text(f"{intertransaction[4]}", color=self.theme.text_primary, size=12),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                        ft.Row([
                            ft.Text(f"{intertransaction[1]}", color=self.theme.text_primary, size=12),
                            ft.Icon(icons.SYNC_ALT, color=self.theme.green_color, size=20),
                            ft.Text(f"{intertransaction[2]}", color=self.theme.text_primary, size=12),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                    ]),
                    alignment=ft.alignment.center,
                    bgcolor=self.theme.fg,
                    border_radius=20,
                    padding=10
                )
            )
        self.page.update()


    def draw(self, header: HeaderSection):
        

        self.accounts = ActiveController.controller_fetch_actives()

        self.header = header.create("Intertransferencia de Activos", return_page=True)

        self.hint_text = ft.Text("Selecciona la cuenta origen y la cuenta destino", color=self.theme.text_primary, size=12)
        
        self.account_from = ft.Dropdown(
            hint_text="Cuenta origen",
            hint_style=ft.TextStyle(color=self.theme.text_primary),
            text_style=ft.TextStyle(color=self.theme.green_color),
            border=ft.InputBorder.OUTLINE,
            bgcolor=self.theme.fg,
            filled=True,
            on_change=self.validate_accounts,
            border_radius=20,
            expand=True
        )

        for account in self.accounts:
            self.account_from.options.append(
                ft.dropdown.Option(
                    key=str(account[0]),
                    text=f"{account[2]} ${account[3]:.2f}"
                )
            )

        self.account_to = ft.Dropdown(
            hint_text="Cuenta destino",
            hint_style=ft.TextStyle(color=self.theme.text_primary),
            text_style=ft.TextStyle(color=self.theme.green_color),
            border=ft.InputBorder.OUTLINE,
            bgcolor=self.theme.fg,
            filled=True,
            on_change=self.validate_accounts,
            border_radius=20,
            expand=True
        )

        for account in self.accounts:
            self.account_to.options.append(
                ft.dropdown.Option(
                    key=str(account[0]),
                    text=f"{account[2]} ${account[3]:.2f}"
                )
            )

        self.intermediate_icon = ft.Icon(
            icons.SYNC_ALT,
            color=self.theme.green_color,
            size=24
        )
        self.account_from.col = {"sm": 12, "md": 5}

        self.account_to.col = {"sm": 12, "md": 5}

        self.account_dropdown_container = ft.Container(
            content=ft.ResponsiveRow([
                self.account_from,
                ft.Container(
                    content=self.intermediate_icon,
                    alignment=ft.alignment.center,
                    col={"sm": 12, "md": 2}
                ),
                self.account_to
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            bgcolor=self.theme.fg,
            border_radius=20,
            padding=15
        )

        self.spawn_error = ft.Text("", color=self.theme.red_color, size=12)

        self.quantity_field = ft.TextField(
            hint_text="Cantidad",
            hint_style=ft.TextStyle(color=self.theme.text_primary),
            text_style=ft.TextStyle(color=self.theme.green_color),
            border=ft.InputBorder.OUTLINE,
            prefix_icon=icons.ATTACH_MONEY,
            bgcolor=self.theme.fg,
            filled=True,
            border_radius=20,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$"),
            on_change=self.validate_quantity,
            error_text="",
        )

        self.intertransactions_container = ft.Container(
            ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE),
            expand=True
        )

        self.transfer_button = ft.Container(
            content=ft.Row([ft.Icon(icons.SEND, color=self.theme.bg), ft.Text("Intertransferir", color=self.theme.bg, size=16, weight=ft.FontWeight.BOLD)], alignment=ft.alignment.center),
            bgcolor=self.theme.green_color,
            padding=15,
            border_radius=20,
            alignment=ft.alignment.center,
            on_click=self.intertransfer,
            disabled=True
        )

        self.add_intertransactions()


        return ft.Container(
            ft.Column([
                self.header,
                self.hint_text,
                self.account_dropdown_container,
                self.spawn_error,
                self.quantity_field,
                self.intertransactions_container,
                self.transfer_button,
            ]),
            margin=ft.margin.symmetric(horizontal=20),
            bgcolor=self.theme.bg,
            expand=True,
        )