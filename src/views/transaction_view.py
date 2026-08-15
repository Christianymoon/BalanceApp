import flet as ft
from flet import Icons as icons

from components.dialogs import Dialogs
from controllers.actives.controller import ActiveController
from controllers.categories.controller import CategoriesController
from controllers.transactions.controller import TransactionController, TransactionType
from dto.transactions import TransactionDTO
from themes.themes import Theme


class TransactionSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.add_transaction = None
        self.categories = []
        self.categories_controller = CategoriesController()

    def parse_transaction_data(self):
        try:
            category_id = self.categories_controller.get_category_by_subcategory_id(
                int(self.add_transaction.content.controls[1].value))[0]
            transaction = TransactionDTO(
                name=self.add_transaction.content.controls[0].value,
                category=category_id,
                subcategory=int(
                    self.add_transaction.content.controls[1].value),
                price=float(self.add_transaction.content.controls[2].value),
                type=self.radiogroup_ref.current.value,
                account_id=self.add_transaction.content.controls[4].value,
            )
            return transaction
        except:
            raise ValueError("Faltan datos por llenar")

    def add_to_database(self, e):
        try:
            transaction = self.parse_transaction_data()
            TransactionController.create_transaction(transaction)
            self.page.go("/")

        except Exception as e:
            Dialogs.error_dialog(self.page, str(e))

    def handle_submit_animation(self, e):
        import time
        e.control.scale = 0.92
        e.control.update()
        time.sleep(0.15)
        e.control.scale = 1.0
        e.control.update()
        self.add_to_database(e)

    def radio_group_event(self, e):
        if e.control.value == "credit":
            self.add_transaction.content.controls[4].disabled = True
        else:
            self.add_transaction.content.controls[4].disabled = False
        self.page.update()

    def draw_option_box(self):
        options = []
        prev_category_id = 0
        for subcategory in self.categories_controller.fetch_all_subcategories():
            # if category is different from prev_category_id filter subcategory
            current_category_id = subcategory[1]
            if subcategory[3] != 0 and current_category_id == prev_category_id:
                options.append(
                    ft.dropdown.Option(text=subcategory[2], key=subcategory[0],
                                       style=ft.TextStyle(color=self.theme.text_primary))
                )
            elif subcategory[3] != 0 and current_category_id != prev_category_id:
                category_name = subcategory[4]
                options.append(ft.dropdown.Option(
                    text=category_name, key=None, style=ft.TextStyle(color=self.theme.blue_color, size=20), disabled=True))
                options.append(
                    ft.dropdown.Option(text=subcategory[2], key=subcategory[0],
                                       style=ft.TextStyle(color=self.theme.text_primary))
                )
            prev_category_id = current_category_id
        return options

    def draw(self, header):
        self.accounts_actives = ActiveController.controller_fetch_actives()

        self.radiogroup_ref = ft.Ref[ft.RadioGroup]()

        self.header = header.create("Transacciones", return_page=True)

        self.add_transaction = ft.Container(
            ft.Column([
                # Name 0
                ft.TextField(
                    hint_text="Nombre",
                    hint_style=ft.TextStyle(color=self.theme.text_secondary),
                    text_style=ft.TextStyle(color=self.theme.text_primary),
                    border=ft.InputBorder.OUTLINE,
                    prefix_icon=icons.PERSON,
                    bgcolor=self.theme.fg,
                    border_radius=20,
                    filled=True,
                ),
                # Category 1
                ft.Dropdown(
                    hint_text="Categoria",
                    options=self.draw_option_box(),
                    text_style=ft.TextStyle(color=self.theme.green_color),
                    hint_style=ft.TextStyle(color=self.theme.text_secondary),
                    border_radius=20,
                    fill_color=self.theme.fg,
                    filled=True,
                    dense=False,
                    expand=True,
                    border=ft.InputBorder.OUTLINE,
                    menu_height=300,
                ),
                # Mount 2
                ft.TextField(
                    hint_text="Monto",
                    hint_style=ft.TextStyle(color=self.theme.text_secondary),
                    text_style=ft.TextStyle(color=self.theme.text_primary),
                    border=ft.InputBorder.OUTLINE,
                    prefix_icon=icons.ATTACH_MONEY,
                    bgcolor=self.theme.fg,
                    border_radius=20,
                    filled=True,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    input_filter=ft.InputFilter(
                        allow=True, regex_string=r"^\d*\.?\d*$"),
                ),
                # Type 3
                ft.RadioGroup(
                    ref=self.radiogroup_ref,
                    value=TransactionType.SPENT.value,
                    content=ft.Row([
                        ft.Radio(value=TransactionType.SPENT.value, label="Gasto",
                                 label_style=ft.TextStyle(color=self.theme.text_primary), hover_color=self.theme.text_secondary, fill_color=self.theme.text_primary),
                        ft.Radio(value=TransactionType.INCOME.value, label="Ingreso",
                                 label_style=ft.TextStyle(color=self.theme.text_primary), hover_color=self.theme.text_secondary, fill_color=self.theme.text_primary),
                        ft.Radio(value=TransactionType.CREDIT.value, label="Credito",
                                 label_style=ft.TextStyle(color=self.theme.text_primary), hover_color=self.theme.text_secondary, fill_color=self.theme.text_primary)
                    ]),
                    on_change=self.radio_group_event,
                ),
                # Account 4
                ft.Dropdown(
                    hint_text="Cuenta origen",
                    options=[ft.dropdown.Option(text=f"{account[2]} ${account[3]:.2f}", key=account[0])
                             for account in self.accounts_actives if account[4]],
                    text_style=ft.TextStyle(color=self.theme.green_color),
                    hint_style=ft.TextStyle(color=self.theme.text_secondary),
                    border_radius=20,
                    fill_color=self.theme.fg,
                    filled=True,
                    dense=False,
                    expand=True,
                    border=ft.InputBorder.OUTLINE,
                )
            ], expand=True),
            bgcolor=self.theme.bg,
        )

        transaction_button = ft.Row([
            ft.CupertinoButton(
                text="Transaccionar",
                icon=icons.DOUBLE_ARROW,
                icon_color=self.theme.fg,
                color=self.theme.fg,
                bgcolor=self.theme.text_primary,
                border_radius=20,
                on_click=self.handle_submit_animation,
                focus_color=self.theme.text_primary,
                expand=True,
                scale=1.0,
                animate_scale=ft.Animation(
                    150, ft.AnimationCurve.EASE_OUT_CUBIC),
            )
        ])

        return ft.Container(
            ft.Column([
                self.header,
                self.add_transaction,
                transaction_button,
            ]),
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
            expand=True,
        )
