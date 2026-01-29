from themes.themes import Theme
import flet as ft


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
