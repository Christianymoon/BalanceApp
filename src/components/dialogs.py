import flet as ft

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

    def error_dialog(page: ft.Page, error: str):
        error_dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(error),
            actions=[ft.TextButton(
                "OK", on_click=lambda e: page.close(error_dialog))],
        )
        return page.open(error_dialog)
