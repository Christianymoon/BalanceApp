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

    @staticmethod
    def info_dialog(page: ft.Page, text: str, content=None, actions=None):
        info_dialog = ft.CupertinoAlertDialog(
            title=ft.Text(text),
            content=content,
            actions=actions
        )
        return page.open(info_dialog)

    @staticmethod
    def confirmation_dialog(page: ft.Page, text: str, content: ft.Control = None, on_confirm: callable = None, on_cancel: callable = None):
        dialog = ft.AlertDialog(
            title=ft.Text(text),
            content=content,
        )

        def handle_cancel(e):
            if on_cancel:
                on_cancel(e)
            page.close(dialog)

        def handle_confirm(e):
            if on_confirm:
                on_confirm(e)
            page.close(dialog)

        dialog.actions = [
            ft.TextButton("Cancelar", on_click=handle_cancel),
            ft.TextButton("Confirmar", on_click=handle_confirm)
        ]
        page.open(dialog)
        return dialog

    @staticmethod
    def error_dialog(page: ft.Page, error: str):
        error_dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(error),
            actions=[ft.TextButton(
                "OK", on_click=lambda e: page.close(error_dialog))],
        )
        return page.open(error_dialog)
