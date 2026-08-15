import flet as ft

from controllers.balance.controller import BalanceController
from controllers.chart import ChartGenerator
from themes.themes import Theme


class BalanceSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.chart_generator = ChartGenerator()
        self.balance_content = None
        days = []
        balance = []
        for item in BalanceController.fetch_snapshots():
            days.append(item[2])
            balance.append(float(item[1]))

        self.last_chart_route = self.chart_generator.balance_chart(
            days=days,
            balance=balance
        )

    def draw(self, header):
        self.balance_content = ft.Column([
            header.create("Balance", return_page=True),
            ft.Column([
                ft.Text("Balance Actual",
                        color=self.theme.text_secondary, size=24),
                ft.Text(f"{BalanceController.controller_fetch_balance(formated=True)}",
                        color=self.theme.text_primary, size=32, weight=ft.FontWeight.BOLD),
                ft.Text(
                    f"Ultima actualizacion: {BalanceController.fetch_last_date_snapshot()}", color=self.theme.text_secondary, size=14),
                ft.Image(
                    src=self.last_chart_route,
                    width=700,
                    fit=ft.ImageFit.CONTAIN,
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        return self.balance_content
