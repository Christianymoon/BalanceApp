from datetime import date

import flet as ft
from flet import Icons as icons

from components.headers import HeaderSection
from controllers.categories.controller import CategoriesController
from controllers.date_groups import create_week_separator, get_group_date
from controllers.transactions.controller import TransactionController
from dto.transactions import TransactionFilterDTO, TransactionOutputDTO
from themes.themes import Theme


class AllTransactionsView:
    def __init__(self, theme: Theme, page: ft.Page):
        self.page = page
        self.theme = theme
        filter = TransactionFilterDTO()  # get all transaction without filter
        self.transactions = TransactionController.fetch_transactions(filter)
        self.categories_controller = CategoriesController()
        self.previous_date = None

    def calculate_period_time(self, date: str = None, timelapse: str = "week"):
        week_start = get_group_date(date=date, timelapse=timelapse)
        if week_start != self.previous_date:
            self.previous_date = week_start
            self.transactions_list.controls.append(
                create_week_separator(week_start, self.theme))

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
                        color=self.theme.text_primary,
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

    def _remove_ring(self):
        if self.ring_animation and self.ring_animation in self.transactions_list.controls:
            self.transactions_list.controls.remove(self.ring_animation)
            self.ring_animation = None

    def _set_ring(self):
        return ft.Container(
            content=ft.ProgressRing(
                expand=True, color=self.theme.text_primary),
            alignment=ft.alignment.center,
            expand=True,
        )

    def _charge_transactions_list(self):
        self.ring_animation = self._set_ring()
        self.transactions_list.controls.append(self.ring_animation)
        for transaction in self.transactions:
            self.calculate_period_time(
                date=transaction.created_at, timelapse="week")
            self.transactions_list.controls.append(
                self._create_transaction_item(transaction))
        self._remove_ring()
        self.page.update()

    def draw(self, header: HeaderSection) -> ft.Container:
        self.transactions_list = ft.Column(
            [],
            spacing=0,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
        )

        self.page.run_thread(
            self._charge_transactions_list
        )

        return ft.Container(
            content=ft.Column([
                header.create(placeholder="Transacciones",
                              return_page=True, config=False),
                self.transactions_list,
            ], expand=True),
            expand=True,
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
        )
