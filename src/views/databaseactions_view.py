import flet as ft


from controllers.controller import DatabaseController
from controllers.categories.controller import CategoriesController
from controllers.transactions.controller import TransactionController
from components.dialogs import Dialogs
from themes.themes import Theme


class DatabaseActionsView:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.db_controller = DatabaseController()
        self.transaction_controller = TransactionController()
        self.category_controller = CategoriesController()

    def delete_categories(self, e):
        def delete(e):
            success = self.category_controller.delete_all_categories()
            if success:
                self.page.open(ft.SnackBar(
                    content=ft.Text("Categorías eliminadas exitosamente")
                ))
            else:
                self.page.open(ft.SnackBar(
                    content=ft.Text("Error al eliminar las categorías")
                ))

        Dialogs.confirmation_dialog(
            self.page,
            "Eliminar categorias",
            ft.Text("¿Estás seguro de que quieres eliminar las categorías?"),
            on_confirm=delete
        )

    def delete_transactions(self, e):

        def delete(e):
            success = self.transaction_controller.delete_all_transactions()
            if success:
                self.page.open(ft.SnackBar(
                    content=ft.Text("Transacciones eliminadas exitosamente")
                ))
            else:
                self.page.open(ft.SnackBar(
                    content=ft.Text("Error al eliminar las transacciones")
                ))

        Dialogs.confirmation_dialog(
            self.page,
            "Eliminar transacciones",
            ft.Text("¿Estás seguro de que quieres eliminar las transacciones?"),
            on_confirm=delete
        )

    def delete_database(self, e):

        def delete(e):
            self.db_controller.reset()
            self.page.open(ft.SnackBar(
                content=ft.Text("Base de datos restaurada exitosamente")
            ))

        Dialogs.confirmation_dialog(
            self.page,
            "Eliminar base de datos",
            ft.Text("¿Estás seguro de que quieres eliminar la base de datos?"),
            on_confirm=delete
        )

    def _database_actions_card(self, icon: ft.Icon = None, title: str = "", callback=None, action_icon=None):
        action = ft.Row(
            controls=[
                ft.IconButton(
                    icon=action_icon,
                    icon_color=self.theme.text_primary,
                    bgcolor=self.theme.bg,
                    on_click=callback
                )
            ],
            alignment=ft.MainAxisAlignment.END,
            expand=True
        )
        return ft.Container(
            content=ft.Row([
                ft.Container(content=icon),
                ft.Text(value=title),
                action,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=self.theme.fg,
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=20, vertical=10)
        )

    def draw(self, header):
        header = header.create("Bases de datos", return_page=True)

        actions_column = ft.Column(

            [
                self._database_actions_card(
                    icon=ft.Icon(ft.Icons.COMPARE_ARROWS,
                                 color=self.theme.text_primary),
                    title="Restaurar transacciones",
                    callback=self.delete_transactions,
                    action_icon=ft.Icons.DELETE
                ),

                self._database_actions_card(
                    icon=ft.Icon(ft.Icons.CATEGORY,
                                 color=self.theme.text_primary),
                    title="Restaurar categorías",
                    callback=self.delete_categories,
                    action_icon=ft.Icons.DELETE
                ),

                ft.Text("DANGER ZONE", size=11,
                        weight=ft.FontWeight.BOLD, color=self.theme.red_color),
                ft.Divider(
                    color=self.theme.text_primary,
                ),

                self._database_actions_card(
                    icon=ft.Icon(ft.Icons.STORAGE,
                                 color=self.theme.text_primary),
                    title="Restaurar base de datos",
                    callback=self.delete_database,
                    action_icon=ft.Icons.DELETE
                ),


            ]
        )

        return ft.Container(
            ft.Column([
                header,
                actions_column
            ]),
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
            expand=True,
        )
