import logging

import flet as ft

from setup import log_dir
from controllers.controller import DatabaseController, UserDataController
from controllers.balance.controller import BalanceController
from client.client import ClientStorage
from themes.themes import LigthMode, DarkMode
from router import navigate_to


from core.config import ASSETS_DIR


class FinanceApp:
    def __init__(self, page: ft.Page):
        self.page = page
        # self.notification_manager = NotificationManager()
        self.client = ClientStorage(self.page)
        dark_mode = self.client.get_value("dark_mode")
        if dark_mode is None:
            dark_mode = True
            self.client.set_value("dark_mode", True)

        if dark_mode:
            self.theme = DarkMode()
        else:
            self.theme = LigthMode()
        self.route_history = []  # Historial de rutas para navegación

        self.page.fonts = {
            "SF-Pro": "/fonts/SF-Pro.ttf",
        }
        self.page.theme = ft.Theme(font_family="SF-Pro")
        self.page.title = "Balance"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = self.theme.bg
        self.page.on_route_change = self.route_change
        self.page.run_thread(self._on_mount)

    def _on_mount(self):
        try:
            db = DatabaseController()
            db.create_tables()
            BalanceController.make_snapshot()
            logging.info("Application mounted successfully.")
            logging.info(f"Setup database")
            if UserDataController.controller_fetch_userdata() is None:
                self.page.go("/setup")
            else:
                self.page.go(self.page.route)
        except Exception as e:
            logging.error(
                f"Error during application mount: {e}", exc_info=True)
            self.page.go("/error")

    def route_change(self, route):
        if len(self.route_history) == 0 or self.route_history[-1] != route.route:
            self.route_history.append(route.route)
        navigate_to(self.page, self.theme, route.route)


def main(page: ft.Page):
    FinanceApp(page)


if __name__ == "__main__":
    ft.app(target=main, assets_dir=ASSETS_DIR)
