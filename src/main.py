import flet as ft
from flet import Icons as icons
from setup import log_dir
from controller import (
    DatabaseController, 
    LiquidController, 
    PassiveController, 
    SearchController, 
    TransactionController, 
    BalanceController, 
    ActiveController,
    UserDataController,
    LoanController
    )

import os
import logging
from datetime import datetime

class Theme:
    bg = "#1a1a1a"
    fg = "#2a2a2a"
    text_primary = "#FFFFFF"
    text_secondary = "#888888"
    green_color = "#00ff88"
    red_color = "#ff4444"

class Dialogs:
    def __init__(self, page: ft.Page):
        self.page = page

    @staticmethod
    def lost_data_dialog(page: ft.Page):
        lost_data_dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text("Por favor completa todos los campos."),
            actions=[ft.TextButton(
                "OK", on_click=lambda e: page.close(lost_data_dialog))],
        )
        return page.open(lost_data_dialog)

class HeaderSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.header = None
        self.file_picker = ft.FilePicker(
            on_result=self.change_background,

        )
        self.page.overlay.append(self.file_picker)

    def change_background(self, e):
        if e.files:
            file = e.files[0]
            img_path = file.path
            self.page.client_storage.remove("christianymoon.finance.profile_pic")
            self.page.client_storage.set("christianymoon.finance.profile_pic", img_path)
            self.header.content.controls[0].content.src = self.page.client_storage.get("christianymoon.finance.profile_pic")
            self.page.update()

    def create(self, placeholder="Bienvenido de nuevo", return_page=True, config=False):
        self.header = ft.Container(
            content=ft.Row([
                ft.Text(placeholder, color=self.theme.text_primary,size=18, weight=ft.FontWeight.W_500, expand=True),
                # ft.Container(width=40, border=ft.border.all(1, "purple"),),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            margin=ft.margin.only(top=25),
            padding=ft.padding.symmetric(vertical=10),
            bgcolor="#000000"
        )

        
        if config:
            self.header.content.controls.append(ft.IconButton(icons.SETTINGS, icon_color=self.theme.text_secondary, icon_size=20, on_click=lambda e: self.page.go("/settings")))

        if not return_page:
            # CREATE PROFILE PICTURE
            self.header.content.controls.insert(0,
                ft.Container(content=ft.Image("./assets/avatar/profile.png", fit=ft.ImageFit.COVER, width=45, height=45),
                            width=45,
                            height=45,
                            # border=ft.border.all(1, "purple"),
                            # padding=4,
                            border_radius=ft.border_radius.all(40),
                            on_click=self.file_picker.pick_files)
                )
            
            # CHANGE PIC IF USER PICK IMAGE
            if self.page.client_storage.contains_key("christianymoon.finance.profile_pic"):
                self.header.content.controls[0].content.src = self.page.client_storage.get("christianymoon.finance.profile_pic")
                self.page.update()

            self.header.padding = ft.padding.symmetric(horizontal=20, vertical=10)
            self.userdata = UserDataController.controller_fetch_userdata()
            if self.userdata[2] == "Femenino":
                self.header.content.controls[1].value = f"Bienvenida de nuevo, {self.userdata[1]}!"
            elif self.userdata[2] == "Masculino":
                self.header.content.controls[1].value = f"Bienvenido de nuevo, {self.userdata[1]}!"

        if return_page:
            self.header.content.controls.insert(0,
                                           ft.IconButton(
                                               icon=icons.ARROW_BACK_IOS,
                                               icon_color=self.theme.text_primary,
                                               icon_size=20,
                                               on_click=lambda e: self.page.go(
                                                   "/")
                                           )
                                           )

        return self.header

class Setup:
    def __init__(self, page: ft.Page):
        self.page = page
        self.theme = Theme()
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

    def draw(self):
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
        return ft.Column(
            [
                header.create("Configuracion", return_page=True),
                ft.Row([
                        ft.CupertinoSwitch(
                            value=self.in_out_mode_value,
                            scale=0.6,
                            key="in_out_mode",
                            on_change=self.handle_in_out_mode,
                        ),

                        ft.Text("Modo solo transacciones")
                    ]
                ),
                ft.ElevatedButton(
                    "Reiniciar Base de Datos",
                    bgcolor=self.theme.red_color,
                    color="#000000",
                    on_click=self.handle_reset_database
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=0, scroll=ft.ScrollMode.ADAPTIVE, expand=True)

class TransactionSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.add_transaction = None

    def add_transaction_database(self, e):
        name = self.add_transaction.content.controls[0].value
        category = self.add_transaction.content.controls[1].value
        price = self.add_transaction.content.controls[2].value
        account_id = self.add_transaction.content.controls[3].value
        is_income = self.add_transaction.content.controls[4].value

        if price == "" or name == "" or category == "" or account_id is None:
            return Dialogs.lost_data_dialog(self.page)
        TransactionController.controller_set_transaction(
            name, category, price, is_income, account_id)

        self.page.go("/")

    def draw(self, header):
        self.accounts_actives = ActiveController.controller_fetch_actives()
        self.add_transaction = ft.Container(
            content=ft.Column([
            ft.TextField(
                hint_text="Nombre",
                hint_style=ft.TextStyle(color=self.theme.text_secondary),
                text_style=ft.TextStyle(color=self.theme.text_primary),
                border=ft.InputBorder.NONE,
                prefix_icon=icons.PERSON,
                bgcolor=self.theme.fg,
                filled=True,
            ),
            ft.TextField(
                hint_text="Categoria",
                hint_style=ft.TextStyle(color=self.theme.text_secondary),
                text_style=ft.TextStyle(color=self.theme.text_primary),
                border=ft.InputBorder.NONE,
                prefix_icon=icons.FILTER,
                bgcolor=self.theme.fg,
                filled=True,
            ),
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
            ft.Dropdown(
                hint_text="Cuenta origen",
                options=[ft.dropdown.Option(text=f"{account[2]} ${account[3]}", key=account[0]) for account in self.accounts_actives if account[4]],
                text_style=ft.TextStyle(color=self.theme.green_color),
                bgcolor=self.theme.fg,
                filled=True,
                border=ft.InputBorder.NONE,
            ),
            ft.Checkbox(label="Suma Capital", value=False),
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
            ])
        )
        return ft.Column([
            header.create("Transacciones", return_page=True),
            self.add_transaction,
        ], spacing=0, scroll=ft.ScrollMode.AUTO)

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

class PassiveSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.passives_selected = []
        self.new_passive = None
        self.passive_list = None

    def add_passive_database(self, e):
        name = self.new_passive.content.controls[0].value
        category = self.new_passive.content.controls[1].value
        price = self.new_passive.content.controls[2].value
        is_liquidated = self.new_passive.content.controls[3].value
        if price == "" or name == "" or category == "":
            return Dialogs.lost_data_dialog(self.page)
        PassiveController.controller_set_passive(
            name, category, price, is_liquidated)
        self.refresh_passives()

    def parse_selected_passives(self, e):
        id = e.control.data
        if id in self.passives_selected:
            self.passives_selected.remove(id)
        else:
            self.passives_selected.append(id)

    def delete_passive(self, e):
        for id in self.passives_selected:
            PassiveController.controller_delete_passive(id)
        self.refresh_passives()

    def liquidate_passive(self, e):
        for id in self.passives_selected:
            PassiveController.liquidate_passive(id)
        self.refresh_passives()

    def refresh_passives(self, *args):
        self.passive_list.controls.clear()
        self.add_passive_list(PassiveController.controller_fetch_passives())
        self.page.update()

    def add_passive_list(self, passives_list):
        self.passive_list.controls.clear()
        for item in reversed(passives_list):
            if item[4]:
                trend_icon = icons.CHECK_CIRCLE
                trend_color = self.theme.green_color
            else:
                trend_icon = icons.ERROR
                trend_color = self.theme.red_color
            self.passive_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Checkbox(
                            value=item[4], on_change=self.parse_selected_passives, data=item[0]),
                        ft.Container(
                            content=ft.Icon(icons.TRENDING_DOWN,
                                            color=self.theme.text_primary, size=24),
                            width=40,
                            height=40,
                            bgcolor=self.theme.fg,
                            border_radius=20,
                            alignment=ft.alignment.center
                        ),
                        ft.Column([
                            ft.Text(item[1], color=self.theme.text_primary,
                                    size=14, weight=ft.FontWeight.W_500),
                            ft.Text(
                                item[2], color=self.theme.text_secondary, size=12)
                        ], spacing=2, expand=True),
                        ft.Container(
                            content=ft.Icon(
                                trend_icon, color=trend_color, size=20),
                            width=30,
                            height=20
                        ),
                        ft.Column([
                            ft.Text(
                                f"${item[3]:.2f}", color=self.theme.text_primary, size=14, weight=ft.FontWeight.W_500),
                            ft.Text(
                                "Pagado" if item[4] else "Aun sin pagar", color=trend_color, size=12)
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=10, vertical=15),
                    bgcolor="#000000"
                )
            )

    def draw(self, header):
        self.new_passive = ft.Container(
            content=ft.Column([
                ft.TextField(
                    hint_text="Nombre",
                    hint_style=ft.TextStyle(color=self.theme.text_secondary),
                    text_style=ft.TextStyle(color=self.theme.text_primary),
                    border=ft.InputBorder.NONE,
                    prefix_icon=icons.PERSON,
                    bgcolor=self.theme.fg,
                    filled=True,
                ),
                ft.TextField(
                    hint_text="Categoria",
                    hint_style=ft.TextStyle(color=self.theme.text_secondary),
                    text_style=ft.TextStyle(color=self.theme.text_primary),
                    border=ft.InputBorder.NONE,
                    prefix_icon=icons.FILTER,
                    bgcolor=self.theme.fg,
                    filled=True,
                ),
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
                ft.Checkbox(label="Pagado", value=False),
                ft.Row([
                    ft.IconButton(
                        icon=icons.HANDSHAKE,
                        icon_color=self.theme.text_primary,
                        on_click=self.add_passive_database,
                        icon_size=24
                    ),
                    ft.Text("Agregar Pasivo", color=self.theme.text_primary,
                            size=14, weight=ft.FontWeight.W_500)
                ]),
            ]), padding=ft.padding.symmetric(vertical=0, horizontal=10)
        )

        passive_controls = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=icons.PAID,
                    icon_color=self.theme.green_color,
                    tooltip="Pagar Pasivo",
                    on_click=self.liquidate_passive,
                    icon_size=24,
                ),
                ft.IconButton(
                    icon=icons.DELETE,
                    icon_color=self.theme.red_color,
                    tooltip="Eliminar Pasivo(s)",
                    on_click=self.delete_passive,
                    icon_size=24,
                ),
                ft.IconButton(
                    icon=icons.REFRESH,
                    icon_color=self.theme.text_primary,
                    tooltip="Refrescar Lista",
                    on_click=self.refresh_passives,
                    icon_size=24,
                )
            ],), padding=ft.padding.symmetric(vertical=0, horizontal=10)
        )

        self.passive_list = ft.Column([])
        self.add_passive_list(PassiveController.controller_fetch_passives())

        return ft.Column([
            header.create("Pasivos", return_page=True),
            self.new_passive,
            passive_controls,
            self.passive_list,
        ], spacing=0, scroll=ft.ScrollMode.AUTO, alignment=ft.MainAxisAlignment.CENTER)

class ActiveSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.checkboxes = False
        self.active_list = None
        self.active_section = None
        self.selected_actives = []

    def add_active_database(self, e):
        active_type = self.active_section.controls[2].value
        name = self.active_section.controls[3].value
        amount = self.active_section.controls[4].value
        is_liquid = self.active_section.controls[5].controls[0].value
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
            if item[4]:
                trend_icon = icons.CHECK_CIRCLE
                trend_color = self.theme.green_color
            else:
                trend_icon = icons.ERROR
                trend_color = self.theme.red_color
            self.active_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Checkbox(
                            value=item[4], on_change=self.parse_selected_actives, data=item[0], visible=self.checkboxes),
                        ft.Container(
                            content=ft.Icon(icons.TRENDING_UP,
                                            color=self.theme.text_primary, size=24),
                            width=40,
                            height=40,
                            bgcolor=self.theme.fg,
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
                                trend_icon, color=trend_color, size=20),
                            width=30,
                            height=20
                        ),
                        ft.Column([
                            ft.Text(
                                f"${item[3]:.2f}", color=self.theme.text_primary, size=14, weight=ft.FontWeight.W_500),
                            ft.Text(
                                "Liquido" if item[4] else "No Liquido", color=trend_color, size=12)
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=0, vertical=15),
                    bgcolor="#000000"
                )
            )
        self.page.update()

    def refresh_actives(self, *args):
        self.active_list.controls.clear()
        self.add_active_list(ActiveController.controller_fetch_actives())
        self.page.update()

    def draw(self, header):
        self.active_list = ft.Column(
            [], scroll=ft.ScrollMode.ADAPTIVE, height=400, expand=True)
        self.active_section = ft.Column([
            header.create("Activos", return_page=True),
            ft.Text("Selecciona tipo de activo", color=self.theme.text_primary,
                    size=14, weight=ft.FontWeight.W_500),
            ft.Dropdown(
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
                border=ft.InputBorder.NONE,
            ),
            ft.TextField(
                hint_text="Nombre del activo",
                hint_style=ft.TextStyle(color=self.theme.text_secondary),
                text_style=ft.TextStyle(color=self.theme.text_primary),
                border=ft.InputBorder.NONE,
                prefix_icon=icons.PERSON,
                bgcolor=self.theme.fg,
                filled=True,
            ),
            ft.TextField(
                hint_text="Valor del activo",
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
            ft.Row([
                ft.Checkbox(label="Es liquido", value=False),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
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
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.active_list,
        ],)
        self.add_active_list(ActiveController.controller_fetch_actives())
        return self.active_section

class BorrowSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page


    def get_loan_data(self, e):
        loan_name = self.loan_form.controls[0].value
        loan_amount = self.loan_form.controls[1].value
        loan_interest = self.loan_form.controls[2].value
        source_account = self.loan_form.controls[3].value
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
        LoanController.set(
            loan_data["name"],
            loan_data["amount"],
            loan_data["interest"],
            loan_data["source_account"],
            loan_data["to"],
            loan_data["from"],
        )
        self.page.go("/")

    def get_all_loans(self, list_control):
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
                            ft.Text(loan[1], color=self.theme.text_primary,
                                    size=14, weight=ft.FontWeight.W_500),
                            ft.Text(
                                str(loan[7]), color=self.theme.text_secondary, size=12)
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(
                                f"${loan[2]}", color=self.theme.text_primary, size=14, weight=ft.FontWeight.W_500),
                            ft.Text(f"{loan[3]}%",
                                    color=self.theme.text_secondary, size=12),
                            ft.Text(
                                "Pagado" if loan[6] else "Pendiente", color=self.theme.green_color if loan[6] else self.theme.red_color, size=12)
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=10, vertical=15),
                    bgcolor="#000000",
                    border_radius=10,
                    on_click=lambda e: print("Selected loan")
                )
            )
        self.page.update()
        

    def ui_events(self, e):
        if e.control.value == "bank":
            self.loan_form.controls[3].disabled = True
        else:
            self.loan_form.controls[3].disabled = False
        self.page.update()

    def draw(self, header):
        self.group1_value = ft.Ref[ft.RadioGroup]()
        self.group2_value = ft.Ref[ft.RadioGroup]()
        self.accounts_actives = ActiveController.controller_fetch_actives()
        loan_type_options = ft.Column([
            ft.Text("Prestamo a:", color=self.theme.text_primary,),
            ft.Row([
                ft.RadioGroup(
                    ref=self.group1_value,
                    value="terciary",
                    content=ft.Row([
                        ft.Radio(value="terciary", label="Terceros"),
                    ], spacing=20),
                ),
            ]),


            ft.Text("Desde:", color=self.theme.text_primary,),
            ft.Row([
                ft.RadioGroup(
                    ref=self.group2_value,
                    value="liquidity",
                    content=ft.Row([
                        ft.Radio(value="liquidity", label="Liquidez"),
                        ft.Radio(value="bank", label="Crédito"),
                    ], spacing=20),
                    on_change=self.ui_events,
                ),
            ]),
        ], spacing=0)
           
        self.loan_form = ft.Column([
            ft.TextField(
            hint_text="Nombre del préstamo",
            border=ft.InputBorder.NONE,
            hint_style=ft.TextStyle(color=self.theme.text_secondary),
            text_style=ft.TextStyle(color=self.theme.text_primary),
            prefix_icon=icons.PERSON,
            bgcolor=self.theme.fg,
            filled=True,
            ),
            ft.TextField(
            hint_text="Monto del préstamo",
            hint_style=ft.TextStyle(color=self.theme.text_secondary),
            text_style=ft.TextStyle(color=self.theme.text_primary),
            border=ft.InputBorder.NONE,
            prefix_icon=icons.ATTACH_MONEY,
            bgcolor=self.theme.fg,
            filled=True,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$"),
            ),
            ft.TextField(
            hint_text="Porcentaje de interés (%)",
            value=0,
            hint_style=ft.TextStyle(color=self.theme.text_secondary),
            text_style=ft.TextStyle(color=self.theme.text_primary),
            border=ft.InputBorder.NONE,
            prefix_icon=icons.PERCENT,
            bgcolor=self.theme.fg,
            filled=True,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$"),
            ),
            ft.Dropdown(
                hint_text="Cuenta origen",
                options=[ft.dropdown.Option(text=f"{account[2]} ${account[3]}", key=account[0]) for account in self.accounts_actives if account[4]],
                text_style=ft.TextStyle(color=self.theme.green_color),
                bgcolor=self.theme.fg,
                filled=True,
                border=ft.InputBorder.NONE,
            ),
        ])

        loan_controls = ft.Row([
            ft.TextButton("Agregar", on_click=lambda e: self.set_loan_database(e)),
        ])


        self.loan_list = ft.Column([], spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        self.get_all_loans(self.loan_list)

        #TODO: Set this content scrollable
        return ft.Column([
            header.create("Préstamos", return_page=True),
            loan_type_options,
            ft.Divider(height=1, color="#333333"),
            self.loan_form,
            loan_controls,
            ft.Divider(height=1, color="#333333"),
            self.loan_list,
        ], spacing=15, scroll=ft.ScrollMode.ADAPTIVE, expand=True)

class MainSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.stock_list = None
        self.header = None

    def change_mode(self, e):
        old_value = self.page.client_storage.get("christianymoon.finance.portfolio_mode")
        self.page.client_storage.remove("christianymoon.finance.portfolio_mode")
        self.page.client_storage.set("christianymoon.finance.portfolio_mode", not old_value)

        if self.page.client_storage.get("christianymoon.finance.in_out_mode_setting"):


            if self.page.client_storage.get("christianymoon.finance.portfolio_mode"):
                amount = TransactionController.controller_fetch_sum(True)
                self.portfolio_section.content.controls[0].controls[0].value = "Ingresos"
                self.portfolio_section.content.controls[1].controls[0].value = amount
                self.portfolio_section.content.controls[1].controls[0].color = self.theme.green_color
                
            else:
                amount = TransactionController.controller_fetch_sum(False)
                self.portfolio_section.content.controls[0].controls[0].value = "Gastos"
                self.portfolio_section.content.controls[1].controls[0].value = amount
                self.portfolio_section.content.controls[1].controls[0].color = self.theme.text_primary
                

        else:

            if self.page.client_storage.get("christianymoon.finance.portfolio_mode"):
                liquid_amount = LiquidController.get(
                    formated=True)
                self.portfolio_section.content.controls[0].controls[0].value = "Liquidez"
                self.portfolio_section.content.controls[1].controls[0].value = liquid_amount
                self.portfolio_section.content.controls[1].controls[0].color = self.theme.green_color
                
            else:
                balance_amount = BalanceController.controller_fetch_balance(
                    formated=True)
                self.portfolio_section.content.controls[0].controls[0].value = "Balance"
                self.portfolio_section.content.controls[1].controls[0].value = balance_amount
                self.portfolio_section.content.controls[1].controls[0].color = self.theme.text_primary


        self.page.client_storage.set("christianymoon.finance.portfolio_mode", not old_value)
        self.page.update()

    def on_search(self, e):
        if e.control.value == "log":
            log_file = open(os.path.join(log_dir), "r")
            logs = log_file.read()
            log_file.close()
            logs_ = ft.Text(logs, color=self.theme.text_primary,
                            size=12, expand=True)
            self.stock_list.controls.clear()
            self.stock_list.controls.append(logs_)
            self.page.update()
            return


        filter_list = SearchController.controller_search_transactions(
            e.control.value)
        
        if e.control.value == "":
            self.stock_list.controls.clear()
            self.add_stock_list(
                TransactionController.controller_fetch_transactions()
            )
            self.page.update()
            return
               
        if len(filter_list) > 0:
            self.stock_list.controls.clear()
            self.add_stock_list(filter_list)            
        else:
            self.stock_list.controls.clear()


        self.page.update()

    def add_stock_list(self, transactions):
        for item in reversed(transactions):
            if item[4]:
                trend_icon = icons.TRENDING_UP
                trend_color = self.theme.green_color
            else:
                trend_icon = icons.TRENDING_DOWN
                trend_color = self.theme.red_color
            self.stock_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(icons.SHOPPING_BAG,
                                            color=self.theme.text_primary, size=24),
                            width=40,
                            height=40,
                            bgcolor=self.theme.fg,
                            border_radius=20,
                            alignment=ft.alignment.center
                        ),
                        ft.Column([
                            ft.Text(item[1], color=self.theme.text_primary,
                                    size=14, weight=ft.FontWeight.W_500),
                            ft.Text(
                                item[2], color=self.theme.text_secondary, size=12),
                            ft.Text(
                                item[6], color=self.theme.text_secondary, size=12),
                        ], spacing=2, expand=True),
                        ft.Container(
                            content=ft.Icon(
                                trend_icon, color=trend_color, size=20),
                            width=30,
                            height=20
                        ),
                        ft.Column([
                            ft.Text(
                                f"${item[3]:.2f}", color=self.theme.text_primary, size=14, weight=ft.FontWeight.W_500),
                            ft.Text(f"%{item[5]:.2f}",
                                    color=trend_color, size=12)
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=20, vertical=15),
                    bgcolor="#000000"
                )
            )


    def update(self):
            portfolio_mode = self.page.client_storage.get("christianymoon.finance.portfolio_mode")
            in_out_mode = self.page.client_storage.get("christianymoon.finance.in_out_mode_setting")

            # Obtener color inicial
            init_color = self.theme.green_color if portfolio_mode else self.theme.text_primary

            # --- MODO INGRESOS/GASTOS ---
            if in_out_mode:
                if portfolio_mode:
                    init_text = "Ingresos"
                    init_value = TransactionController.controller_fetch_sum(True)
                else:
                    init_text = "Gastos"
                    init_value = TransactionController.controller_fetch_sum(False)
            # --- MODO BALANCE/LIQUIDEZ ---
            else:
                if portfolio_mode:
                    init_text = "Liquidez"
                    init_value = LiquidController.get(formated=True)
                else:
                    init_text = "Balance"
                    init_value = BalanceController.controller_fetch_balance(formated=True)

            # Actualizar solo los textos internos sin reconstruir todo
            self.portfolio_section.content.controls[0].controls[0].value = init_text
            self.portfolio_section.content.controls[1].controls[0].value = str(init_value)
            self.portfolio_section.content.controls[1].controls[0].color = init_color
            self.page.update()

    def draw(self, header):
        self.header = header
        search_bar = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icons.SEARCH,
                            color=self.theme.text_secondary, size=20),
                    ft.TextField(
                        hint_text="Buscar transaccion",
                        hint_style=ft.TextStyle(
                            color=self.theme.text_secondary),
                        text_style=ft.TextStyle(color=self.theme.text_primary),
                        border=ft.InputBorder.NONE,
                        expand=True,
                        cursor_color=self.theme.text_primary,
                        on_change=self.on_search,
                    ),

                    
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=0),
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
            bgcolor=self.theme.fg,
            border_radius=30,
            border=ft.border.all(1, "#333333"),
        )

        # Usar height=400 fija la altura en píxeles, pero no es adaptable a todos los dispositivos.
        # Para que el contenido se ajuste dinámicamente al alto disponible, usa expand=True y elimina height.
        # Ejemplo adaptable:

        self.stock_list = ft.Column(
            [], spacing=0, scroll=ft.ScrollMode.ADAPTIVE, expand=True
        )
        self.add_stock_list(
            TransactionController.controller_fetch_transactions())

        init_color = self.theme.green_color if self.page.client_storage.get("christianymoon.finance.portfolio_mode") else self.theme.text_primary
        init_text = ""
        init_value = 0


        if self.page.client_storage.get("christianymoon.finance.in_out_mode_setting"):
            
            if self.page.client_storage.get("christianymoon.finance.portfolio_mode"):
                init_text = "Ingresos" 
                init_value = TransactionController.controller_fetch_sum(True)

            else:
                init_text = "Gastos"
                init_value = TransactionController.controller_fetch_sum(False)
                
            
            self.portfolio_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(init_text, color=self.theme.text_primary, size=14),
                    ft.CupertinoSwitch(
                        value=self.page.client_storage.get("christianymoon.finance.portfolio_mode"),
                        scale=0.6,
                        key="switch",
                        on_change=self.change_mode
                    ),
                ]),
                ft.Row([
                    ft.Text(f"{init_value}",
                            color=init_color, size=32, weight=ft.FontWeight.BOLD),
                    # ft.IconButton(icons.EDIT, icon_color=self.theme.text_primary, icon_size=20,
                    #               on_click=lambda e: self.page.go("/balance")),
                ], spacing=10),
            ], spacing=5),
            padding=ft.padding.symmetric(horizontal=20, vertical=20),
            bgcolor="#000000"
            )
        else:

            if self.page.client_storage.get("christianymoon.finance.portfolio_mode"):
                init_text = "Liquidez" 
                init_value = LiquidController.get(formated=True)
            else:
                init_text = "Balance"
                init_value = BalanceController.controller_fetch_balance(formated=True)
            self.portfolio_section = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(init_text, color=self.theme.text_secondary, size=14),
                        ft.CupertinoSwitch(
                            value=self.page.client_storage.get("christianymoon.finance.portfolio_mode"),
                            scale=0.6,
                            key="switch",
                            on_change=self.change_mode
                        ),
                    ]),
                    ft.Row([
                        ft.Text(f"{init_value}",
                                color=init_color, size=32, weight=ft.FontWeight.BOLD),
                        ft.IconButton(icons.EDIT, icon_color=self.theme.text_primary, icon_size=20,
                                    on_click=lambda e: self.page.go("/balance")),
                    ], spacing=10),
                ], spacing=5),
                padding=ft.padding.symmetric(horizontal=20, vertical=20),
                bgcolor="#000000"
            )

        category_buttons = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.IconButton(icon=icons.TRENDING_UP, icon_color=self.theme.text_primary,
                                  icon_size=24, on_click=lambda e: self.page.go("/active")),
                    ft.Text("Activos", color=self.theme.text_primary, size=12)
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Column([
                    ft.IconButton(icon=icons.PIE_CHART, icon_color=self.theme.text_primary,
                                  icon_size=24, on_click=lambda e: self.page.go("/passive")),
                    ft.Text("Pasivos", color=self.theme.text_primary, size=12)
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Column([
                    ft.IconButton(icon=icons.ATTACH_MONEY, icon_color=self.theme.text_primary, 
                                  icon_size=24, on_click=lambda e: self.page.go("/borrows")),
                    ft.Text("Prestamos", color=self.theme.text_primary, size=12)
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            padding=ft.padding.symmetric(horizontal=20, vertical=20),
            bgcolor="#000000"
        )

        top_picks_header = ft.Container(
            content=ft.Row([
                ft.Text("Operaciones", color=self.theme.text_primary,
                        size=16, weight=ft.FontWeight.W_500),
                ft.Row([ft.IconButton(icon=icons.ADD, icon_color=self.theme.text_primary,
                                      icon_size=24, on_click=lambda e: self.page.go("/transaction"))]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=20, vertical=0),
            bgcolor="#000000"
        )

        return ft.Column([
            header.create(return_page=False, config=True),
            search_bar,
            self.portfolio_section,
            category_buttons,
            top_picks_header,
            self.stock_list
        ], expand=True, spacing=0)

class ErrorPage():
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page

    def draw(self, errors):
        return ft.Column([
            ft.Text("Ha ocurrido un error inesperado.",
                    color=self.theme.red_color, size=24),
            ft.Text("Detalles del error:",
                    color=self.theme.text_primary, size=16),
            ft.Column([
                ft.Text(errors, color=self.theme.text_secondary,
                        size=12, expand=True),
            ], scroll=ft.ScrollMode.AUTO, expand=True),
            ft.ElevatedButton("Volver al inicio", bgcolor=self.theme.green_color,
                              color="#000000", on_click=lambda e: self.page.go("/"))], expand=True)

class FinanceApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.fonts = {
            "SF-Pro": "/fonts/SF-Pro.ttf",
        }
        self.page.theme = ft.Theme(font_family="SF-Pro")  # Default app font
        self.page.on_route_change = self.route_change
        self.page.title = "Balance"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#000000"
        self.page.padding = 0
        self.page.spacing = 0
        self.theme = Theme()
        self.header = HeaderSection(self.theme, page)
        self.transaction_section = TransactionSection(self.theme, page)
        self.balance_section = BalanceSection(self.theme, page)
        self.passive_section = PassiveSection(self.theme, page)
        self.active_section = ActiveSection(self.theme, page)
        self.main_section = MainSection(self.theme, page)
        self.settings_section = Settings(self.theme, page)
        self.error_section = ErrorPage(self.theme, page)
        self.borrow_section = BorrowSection(self.theme, page)
        self.setup_section = None
        self.errors = ""
        self.page.run_thread(self._on_mount)

    def _on_mount(self):
        try:
            db = DatabaseController()
            db.create_tables()
            logging.info("Application mounted successfully.")
            logging.info(f"Setup database")
            if UserDataController.controller_fetch_userdata() is None:
                self.setup_section = Setup(self.page)
                self.page.go("/setup")
            else:
                self.page.go(self.page.route)
        except Exception as e:
            logging.error(
                f"Error during application mount: {e}", exc_info=True)
            self.errors = str(e)
            self.page.go("/error")

    def route_change(self, route):
        try:
            self.page.views.clear()
            if self.page.route == "/setup":
                self.page.views.append(
                    ft.View("/setup", [self.setup_section.draw()], bgcolor="#000000"))
            if self.page.route == "/settings":
                self.page.views.append(
                    ft.View("/settings", [self.settings_section.draw(self.header)], bgcolor="#000000"))
            if self.page.route == "/":
                self.page.views.append(
                    ft.View("/", [self.main_section.draw(self.header)], bgcolor="#000000"))
            if self.page.route == "/transaction":
                self.page.views.append(
                    ft.View("/transaction", [self.transaction_section.draw(self.header)], bgcolor="#000000"))
            if self.page.route == "/balance":
                self.page.views.append(
                    ft.View("/balance", [self.balance_section.draw(self.header)], bgcolor="#000000"))
            if self.page.route == "/passive":
                self.page.views.append(
                    ft.View("/passive", [self.passive_section.draw(self.header)], bgcolor="#000000"))
            if self.page.route == "/active":
                self.page.views.append(
                    ft.View("/active", [self.active_section.draw(self.header)], bgcolor="#000000"))
            if self.page.route == "/borrows":
                self.page.views.append(
                    ft.View("/borrows", [self.borrow_section.draw(self.header)], bgcolor="#000000"))
            if self.page.route == "/error":
                self.page.views.append(
                    ft.View("/error", [self.error_section.draw(self.errors)], bgcolor="#000000"))
            
            self.page.update()
        except Exception as e:
            logging.error(f"Error during route change: {e}", exc_info=True)
            self.errors = str(e)
            self.page.go("/error")
            self.page.update()

def main(page: ft.Page):
    FinanceApp(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
