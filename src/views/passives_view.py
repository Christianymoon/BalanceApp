from controllers.controller import (
    PassiveController,
    ActiveController,
)

from components.headers import HeaderSection
from components.dialogs import Dialogs

from themes.themes import Theme
from flet import Icons as icons
import flet as ft


class PassiveSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.passives_selected = []
        self.new_passive = None
        self.passive_list = None
        self.accounts_actives = ActiveController.controller_fetch_actives()

    def handle_item_view(self, e):
        try:
            self.new_passive = PassiveController.fetch_passive(e.control.data)
            self.page.data = {
                "passive": self.new_passive
            }
            self.page.go("/passive_item")
        except Exception as e:
            Dialogs.error_dialog(self.page, str(e))

    def add_passive_database(self, e):
        name = self.name_field.value
        category = self.category_field.value
        price = self.mount_field.value

        if price == "" or name == "" or category == "":
            return Dialogs.lost_data_dialog(self.page)

        
        PassiveController.controller_set_passive(
            name, category, price)
        self.refresh_passives()

    def refresh_passives(self, *args):
        self.passive_list.controls.clear()
        self.add_passive_list(PassiveController.controller_fetch_passives())
        self.page.update()

    def add_passive_list(self, passives_list):
        self.passive_list.controls.clear()
        for item in reversed(passives_list):
            if item[4]:
                trend_icon = icons.CHECK_CIRCLE
                trend_color = self.theme.green_color
            else:
                trend_icon = icons.ERROR
                trend_color = self.theme.red_color
            self.passive_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(icons.TRENDING_DOWN,
                                            color=self.theme.red_color, size=24),
                            width=40,
                            height=40,
                            bgcolor=self.theme.bg,
                            border_radius=20,
                            alignment=ft.alignment.center
                        ),
                        ft.Column([
                            ft.Text(item[1], color=self.theme.text_primary,
                                    size=14, weight=ft.FontWeight.W_500),
                            ft.Text(
                                item[2], color=self.theme.text_secondary, size=12)
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
                            ft.Text(
                                "Pagado" if item[4] else "Aun sin pagar", color=trend_color, size=12)
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=10, vertical=15),
                    margin=ft.margin.symmetric(vertical=5),
                    border_radius=20,
                    bgcolor=self.theme.fg,
                    on_click=self.handle_item_view,
                    data=item[0]
                )
            )

    def ui_events(self, e):
        if self.is_liquidated_checkbox.value:
            self.dropdown.visible = True
        else:
            self.dropdown.visible = False
        self.page.update()

    def draw(self, header):

        self.header = header.create("Pasivos", return_page=True)

        self.name_field = ft.TextField(
            hint_text="Nombre",
            hint_style=ft.TextStyle(color=self.theme.text_secondary),
            text_style=ft.TextStyle(color=self.theme.text_primary),
            border=ft.InputBorder.OUTLINE,
            prefix_icon=icons.PERSON,
            bgcolor=self.theme.fg,
            filled=True,
            border_radius=20,
            )

        self.category_field = ft.TextField(
                    hint_text="Categoria",
                    hint_style=ft.TextStyle(color=self.theme.text_secondary),
                    text_style=ft.TextStyle(color=self.theme.text_primary),
                    border=ft.InputBorder.OUTLINE,
                    prefix_icon=icons.FILTER,
                    bgcolor=self.theme.fg,
                    filled=True,
                    border_radius=20,
                )

        self.mount_field = ft.TextField(
                    hint_text="Monto",
                    hint_style=ft.TextStyle(color=self.theme.text_secondary),
                    text_style=ft.TextStyle(color=self.theme.text_primary),
                    border=ft.InputBorder.OUTLINE,
                    prefix_icon=icons.ATTACH_MONEY,
                    bgcolor=self.theme.fg,
                    filled=True,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    input_filter=ft.InputFilter(
                        allow=True, regex_string=r"^\d*\.?\d*$"),
                    border_radius=20,
                )

        self.panel = ft.Row([
                    ft.IconButton(
                        icon=icons.HANDSHAKE,
                        icon_color=self.theme.text_primary,
                        on_click=self.add_passive_database,
                        icon_size=24
                    ),
                    ft.Text("Agregar Pasivo", color=self.theme.text_primary,
                            size=14, weight=ft.FontWeight.W_500)
                ])

        self.controls = ft.Row([
                ft.IconButton(
                    icon=icons.REFRESH,
                    icon_color=self.theme.text_primary,
                    tooltip="Refrescar Lista",
                    on_click=self.refresh_passives,
                    icon_size=24,
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.passive_list = ft.Column([], spacing=0, scroll=ft.ScrollMode.AUTO,
            expand=True)

        self.add_passive_list(PassiveController.controller_fetch_passives())

        self.passive_section = ft.Container(
            ft.Column([
                self.header,
                self.name_field,
                self.category_field,
                self.mount_field,
                self.panel,
                self.controls,
                self.passive_list
            ]),
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
            expand=True,
        )

        return self.passive_section



class PassiveItemView():
    def __init__(self, theme: Theme, page: ft.Page):
        self.page = page
        self.theme = theme
        self.current_passive = self.page.data["passive"]
        self.accounts = ActiveController.controller_fetch_actives()

    def pay_passive(self, e):
        if self.account_dropdown.value:
            try:
                PassiveController.pay_passive(self.current_passive[0], self.account_dropdown.value)
                self.page.go("/passive")
            except Exception as e:
                print(e)
                Dialogs.error_dialog(self.page, str(e))
                self.page.update()
        else:
            Dialogs.lost_data_dialog(self.page)
        self.page.update()

    def delete_passive(self, e):
        PassiveController.controller_delete_passive(self.current_passive[0])
        self.page.go("/passive")

    def draw(self, header):

        self.header = header.create("Pasivo", return_page=True)

        self.card = ft.Container(
            ft.Column([
                ft.Text(self.current_passive[1].capitalize(), size=16, weight=ft.FontWeight.W_500),

                ft.Divider(),

                ft.Row(
                    [
                        ft.Text("Categoria: "),
                        ft.Text(self.current_passive[2].capitalize())
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=10
                ),

                ft.Row(
                    [
                        ft.Text("Fecha: "),
                        ft.Text(self.current_passive[5])
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=10
                ),
                

                ft.Row(
                    [
                        ft.Text("Deuda: "),
                        ft.Text("$" + str(self.current_passive[3]))
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=10
                ),


                ft.Row(
                    [
                        ft.Icon(icons.CHECK_CIRCLE if self.current_passive[4] else icons.CANCEL, color=self.theme.green_color if self.current_passive[4] else self.theme.red_color, size=20), 
                        ft.Text("Pagado" if self.current_passive[4] else "Aun sin pagar", size=14)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=10
                ),
                
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=10),
            padding=ft.padding.symmetric(horizontal=10, vertical=15),
            border_radius=20,
            bgcolor=self.theme.fg,
        )

        self.account_dropdown = ft.Dropdown(
            hint_text="Cuenta origen",
            options=[ft.dropdown.Option(text=f"{account[2]} $ {account[3]}", key=account[0]) for account in self.accounts if account[4]], 
            text_style=ft.TextStyle(color=self.theme.green_color),
            bgcolor=self.theme.bg,
            filled=True,
            border=ft.InputBorder.OUTLINE,
            border_radius=20,
            visible=not self.current_passive[4],
        )

        self.hint_text = ft.Text("Al pagar este pasivo, se descontara el monto de la cuenta seleccionada.", color=self.theme.text_secondary, size=12)


        self.pay_button = ft.Container(
            content=ft.Text("Pagar", color=self.theme.bg, size=16, weight=ft.FontWeight.BOLD),
            bgcolor=self.theme.green_color,
            padding=15,
            border_radius=20,
            alignment=ft.alignment.center,
            on_click=self.pay_passive,
            visible=not self.current_passive[4],
        )

        self.delete_button = ft.Container(
            content=ft.Text("Eliminar", color=self.theme.bg, size=16, weight=ft.FontWeight.BOLD),
            bgcolor=self.theme.red_color,
            padding=15,
            border_radius=20,
            alignment=ft.alignment.center,
            visible=self.current_passive[4] == True,
            on_click=self.delete_passive,
        )

        self.space = ft.Container(ft.Column(), expand=True)

        self.button_panel = ft.Row(
            [
                self.pay_button,
                self.delete_button
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10
        )

        return ft.Container(
            ft.Column([
                self.header,
                self.card,
                self.hint_text,
                self.account_dropdown,
                self.space,
                self.button_panel,
            ]),
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
            expand=True,
        )
