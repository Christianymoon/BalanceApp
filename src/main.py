import flet as ft
from flet import Icons as icons
from setup import log_dir
from controllers.controller import DatabaseController
from controllers.controller import UserDataController

from themes.themes import Theme
from router import navigate_to

import logging


class FinanceApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.theme = Theme()
        self.route_history = []  # Historial de rutas para navegación
        
        self.page.fonts = {
            "SF-Pro": "/fonts/SF-Pro.ttf",
        }
        self.page.theme = ft.Theme(font_family="SF-Pro")
        self.page.title = "Balance"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = self.theme.bg
        self.page.on_route_change = self.route_change

        self.page.on_view_pop = self.handle_pop_views 
        self.page.run_thread(self._on_mount)

    def _on_mount(self):
        try:
            db = DatabaseController()
            db.create_tables()
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
        # Agregar la ruta actual al historial si no es la misma que la última
        if len(self.route_history) == 0 or self.route_history[-1] != route.route:
            self.route_history.append(route.route)
        navigate_to(self.page, self.theme, route.route)
    
    def handle_pop_views(self):
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view)


def main(page: ft.Page):
    FinanceApp(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
