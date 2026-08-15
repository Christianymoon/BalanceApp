from datetime import date, timedelta

import flet as ft
from flet import Icons as icons

from client.client import ClientStorage
from controllers.balance.controller import BalanceController
from controllers.categories.controller import CategoriesController
from controllers.controller import SearchController
from controllers.date_groups import create_week_separator, get_group_date
from controllers.liquid.controller import LiquidController
from controllers.transactions.controller import TransactionController
from controllers.transactions.statistics import fetch_summary
from dto.transactions import TransactionFilterDTO, TransactionOutputDTO
from themes.themes import Theme


class MainSection:
    def __init__(self, theme: Theme, page):
        self.theme = theme
        self.page = page
        self.categories_controller = CategoriesController()
        self.storage = ClientStorage(self.page)
        self.portfolio_mode_state = self.storage.get_value("portfolio_mode")
        self.in_out_mode_state = self.storage.get_value("in_out_mode_setting")
        self.previous_date = None

    def change_portfolio_mode(self, e):
        portfolio_model_old_state = self.storage.get_value("portfolio_mode")
        self.storage.set_value("portfolio_mode", not portfolio_model_old_state)
        self.portfolio_mode_state = self.storage.get_value("portfolio_mode")
        self.set_states()

    def calculate_period_time(self, date: str, timelapse: str = None):
        week_start = get_group_date(date, timelapse)
        if self.previous_date != week_start:
            self.previous_date = week_start
            self.transaction_list.controls.append(
                create_week_separator(week_start, self.theme))

    def _charge_transaction_list(self):
        filter = TransactionFilterDTO(limit=30)
        transactions = TransactionController.fetch_transactions(filter)
        for transaction in transactions:
            self.calculate_period_time(
                date=transaction.created_at, timelapse="week")
            self.transaction_list.controls.append(
                self._create_transaction_item(transaction))
        self.page.update()

    def set_states(self):
        if self.in_out_mode_state:
            if self.portfolio_mode_state:
                filter = TransactionFilterDTO(is_income=True)
                amount = fetch_summary(filter)
                self.text_name.value = "Ingresos"
                self.text_amount.value = amount

                self.secondary_text_amount.visible = False

            else:
                filter = TransactionFilterDTO(is_income=False)
                amount = fetch_summary(filter)
                self.text_name.value = "Gastos"
                self.text_amount.value = amount

                self.secondary_text_amount.visible = False

        else:
            if self.portfolio_mode_state:
                liquid_amount = LiquidController.get(formated=True)
                self.text_name.value = "Liquidez"
                self.text_amount.value = liquid_amount

                week_start = get_group_date(
                    date=date.today().strftime("%d/%m/%Y %H:%M"), timelapse="week")
                filter = TransactionFilterDTO(
                    date_from=week_start,
                    date_to=week_start + timedelta(days=6),
                    is_income=True
                )

                self.secondary_text_amount.value = f"Ingreso Semanal: {fetch_summary(filter)}"

            else:
                balance_amount = BalanceController.controller_fetch_balance(
                    formated=True)
                self.text_name.value = "Capital"
                self.text_amount.value = balance_amount

                week_start = get_group_date(
                    date=date.today().strftime("%d/%m/%Y %H:%M"), timelapse="week")
                filter = TransactionFilterDTO(
                    date_from=week_start,
                    date_to=week_start + timedelta(days=6),
                    is_income=False
                )

                self.secondary_text_amount.value = f"Gasto Semanal: {fetch_summary(filter)}"

        self.page.update()

    def on_search(self, e):
        if e.control.value == "":
            self.transaction_list.controls.clear()
            self._charge_transaction_list()
            self.page.update()
            return

        filter_list = SearchController.controller_search_transactions(
            e.control.value)

        if len(filter_list) > 0:
            for transaction in filter_list:
                self.transaction_list.controls.append(
                    self._create_transaction_item(transaction))
        else:
            self.transaction_list.controls.clear()

        self.page.update()

    def _create_transaction_item(self, transaction: TransactionOutputDTO):
        category_name = self.categories_controller.get_category_name(
            transaction.category)
        if transaction.is_income:
            trend_icon = icons.TRENDING_UP
            trend_color = self.theme.green_color
        else:
            trend_icon = icons.TRENDING_DOWN
            trend_color = self.theme.red_color

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(
                        icons.SHOPPING_BAG,
                        color=self.theme.text_secondary,
                        size=24
                    ),
                    width=40,
                    height=40,
                    bgcolor=self.theme.fg,
                    border_radius=20,
                    alignment=ft.alignment.center
                ),
                ft.Column([
                    ft.Text(
                        transaction.name,
                        color=self.theme.text_primary,
                        size=14,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Text(
                        category_name,
                        color=self.theme.text_secondary,
                        size=12
                    ),
                    ft.Text(
                        transaction.created_at,
                        color=self.theme.text_secondary,
                        size=12
                    ),
                ], spacing=2, expand=True),
                ft.Container(
                    content=ft.Icon(
                        trend_icon,
                        color=trend_color,
                        size=20
                    ),
                    width=30,
                    height=20
                ),
                ft.Column([
                    ft.Text(
                        f"${transaction.price:.2f}",
                        color=self.theme.text_primary,
                        size=14,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Text(
                        f"%{transaction.expense_percentage:.2f}",
                        color=trend_color,
                        size=12
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=self.theme.fg,
            border_radius=30,
            margin=ft.margin.symmetric(horizontal=0, vertical=5),
        )

    def _floating_button(self):
        return ft.IconButton(
            icon=icons.ADD,
            icon_color=self.theme.fg,
            bgcolor=self.theme.blue_color,
            on_click=lambda e: self.page.go("/transaction"),
            tooltip="Agregar Transacción",
            width=50,
            height=50,
        )

    def draw(self, header):
        self.header = header

        self.transaction_list = ft.Column(
            [], spacing=0, scroll=ft.ScrollMode.ADAPTIVE, expand=True,
        )

        self.text_name = ft.Text(
            value="", color=self.theme.text_secondary, size=14)

        self.text_amount = ft.Text(
            value="", color=self.theme.text_primary, size=32, weight=ft.FontWeight.BOLD)

        def on_search_focus(e):
            self.search_bar.border = ft.border.only(
                bottom=ft.BorderSide(2, self.theme.blue_color))
            self.search_bar.padding = ft.padding.symmetric(
                horizontal=16, vertical=2)
            self.search_bar.update()

        def on_search_blur(e):
            self.search_bar.border = ft.border.only(
                bottom=ft.BorderSide(1, "#333333"))
            self.search_bar.padding = ft.padding.symmetric(
                horizontal=12, vertical=0)
            self.search_bar.update()

        self.search_bar = ft.Container(
            content=ft.Row(
                [
                    ft.TextField(
                        prefix_icon=icons.SEARCH,
                        hint_text="Buscar transaccion",
                        hint_style=ft.TextStyle(
                            color=self.theme.text_secondary),
                        text_style=ft.TextStyle(color=self.theme.text_primary),
                        border=ft.InputBorder.NONE,
                        text_align=ft.TextAlign.LEFT,
                        expand=True,
                        cursor_color=self.theme.text_primary,
                        on_change=self.on_search,
                        on_focus=on_search_focus,
                        on_blur=on_search_blur,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=0),
            margin=ft.margin.symmetric(horizontal=0, vertical=0),
            animate=ft.Animation(250, ft.AnimationCurve.DECELERATE),
            border=ft.border.only(bottom=ft.BorderSide(1, self.theme.fg)),
        )

        self.secondary_text_amount = ft.Text(
            value="$ 0.00", color=self.theme.text_secondary, size=14)

        self.portfolio_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    self.text_name,
                    ft.CupertinoSwitch(
                        active_track_color=self.theme.blue_color,
                        value=self.portfolio_mode_state,
                        scale=0.6,
                        key="switch",
                        on_change=self.change_portfolio_mode
                    ),
                ]),
                ft.Row([
                    self.text_amount,
                    ft.IconButton(
                        icon=icons.BAR_CHART, icon_color=self.theme.blue_color, icon_size=24, on_click=lambda e: self.page.go("/balance")
                    )
                ], spacing=10),
                ft.Row([
                    self.secondary_text_amount
                ], spacing=10)
            ], spacing=5),
            padding=ft.padding.symmetric(horizontal=20, vertical=20),
            margin=ft.margin.symmetric(horizontal=0, vertical=8),
            bgcolor=self.theme.fg,
            border_radius=30,
        )

        category_buttons = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.IconButton(icon=icons.TRENDING_UP, icon_color=self.theme.text_secondary,
                                  icon_size=24, on_click=lambda e: self.page.go("/active")),
                    ft.Text("Activos", color=self.theme.text_secondary, size=12)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([
                    ft.IconButton(icon=icons.TRENDING_DOWN, icon_color=self.theme.text_secondary,
                                  icon_size=24, on_click=lambda e: self.page.go("/passive")),
                    ft.Text("Pasivos", color=self.theme.text_secondary, size=12)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([
                    ft.IconButton(icon=icons.ACCOUNT_BALANCE, icon_color=self.theme.text_secondary,
                                  icon_size=24, on_click=lambda e: self.page.go("/borrows")),
                    ft.Text("Prestamos", color=self.theme.text_secondary, size=12)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([
                    ft.IconButton(icon=icons.AUTO_AWESOME, icon_color=self.theme.purple_color,
                                  icon_size=24, on_click=lambda e: self.page.go("/ai_chat")),
                    ft.Text("Kara AI", color=self.theme.text_secondary,
                            size=12, text_align=ft.TextAlign.CENTER)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=20, vertical=20),
            margin=ft.margin.symmetric(horizontal=0, vertical=8),
            bgcolor=self.theme.fg,
            border_radius=30,
        )

        top_picks_header = ft.Container(
            content=ft.Row([
                ft.Text("Operaciones", color=self.theme.text_primary,
                        size=16, weight=ft.FontWeight.W_500),
                ft.Row([
                    ft.Container(
                        content=ft.Text(
                            "Ver todo",
                            color=self.theme.blue_color,
                            size=14
                        ),
                        on_click=lambda e: self.page.go("/all_transactions")
                    )
                ]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=10, vertical=0),
            margin=ft.margin.symmetric(horizontal=0, vertical=8),
            bgcolor=self.theme.bg,
            border_radius=30,
        )

        floating_button = self._floating_button()

        self.set_states()

        self.page.run_thread(
            self._charge_transaction_list
        )

        return ft.Container(
            content=ft.Stack([
                ft.Column([
                    header.create(return_page=False, config=True),
                    self.search_bar,
                    self.portfolio_section,
                    category_buttons,
                    top_picks_header,
                    self.transaction_list,
                ], expand=True),
                ft.Container(
                    content=floating_button,
                    right=0,
                    bottom=10,
                    width=50,
                    height=50,
                )
            ], expand=True),
            expand=True,
            margin=ft.margin.symmetric(horizontal=20, vertical=0),
        )
