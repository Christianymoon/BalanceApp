from themes.themes import Theme
from controllers.controller import (
    TransactionController,
    LiquidController,
    BalanceController,
    SearchController
)

import flet as ft
from flet import Icons as icons
import os

class MainSection:
    def __init__(self, theme: Theme, page):
        self.theme = theme
        self.page = page
        self.stock_list = None
        self.portfolio_section = None
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
                    bgcolor=self.theme.fg,
                    border_radius=30,
                    margin=ft.margin.symmetric(horizontal=20, vertical=5),
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
            bgcolor=self.theme.bg,
            border_radius=30,
            border=ft.border.all(1, "#333333"),
        )

        # Usar height=400 fija la altura en píxeles, pero no es adaptable a todos los dispositivos.
        # Para que el contenido se ajuste dinámicamente al alto disponible, usa expand=True y elimina height.
        # Ejemplo adaptable:

        self.stock_list = ft.Column(
            [], spacing=0, scroll=ft.ScrollMode.ADAPTIVE, expand=True,
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
            bgcolor=self.theme.fg,
            border_radius=30,
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
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
                bgcolor=self.theme.fg,
                border_radius=30,
                margin=ft.margin.symmetric(horizontal=20, vertical=10),
            )

        category_buttons = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.IconButton(icon=icons.TRENDING_UP, icon_color=self.theme.text_primary,
                                  icon_size=24, on_click=lambda e: self.page.go("/active")),
                    ft.Text("Activos", color=self.theme.text_primary, size=12)
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Column([
                    ft.IconButton(icon=icons.TRENDING_DOWN, icon_color=self.theme.text_primary,
                                  icon_size=24, on_click=lambda e: self.page.go("/passive")),
                    ft.Text("Pasivos", color=self.theme.text_primary, size=12)
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Column([
                    ft.IconButton(icon=icons.MONETIZATION_ON, icon_color=self.theme.text_primary, 
                                  icon_size=24, on_click=lambda e: self.page.go("/borrows")),
                    ft.Text("Prestamos", color=self.theme.text_primary, size=12)
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            padding=ft.padding.symmetric(horizontal=20, vertical=20),
            bgcolor=self.theme.fg,
            border_radius=30,
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
        )

        top_picks_header = ft.Container(
            content=ft.Row([
                ft.Text("Operaciones", color=self.theme.text_primary,
                        size=16, weight=ft.FontWeight.W_500),
                ft.Row([ft.IconButton(icon=icons.ADD, icon_color=self.theme.text_primary,
                                      icon_size=24, on_click=lambda e: self.page.go("/transaction"))]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=20, vertical=0),
            bgcolor=self.theme.bg,
            border_radius=30,
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
        )

        return ft.Column([
            header.create(return_page=False, config=True),
            search_bar,
            self.portfolio_section,
            category_buttons,
            top_picks_header,
            self.stock_list
        ], expand=True, spacing=0)