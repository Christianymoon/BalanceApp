import flet as ft
from flet import Icons as icons

from components.dialogs import Dialogs
from components.headers import HeaderSection as Header
from components.dialogs import Dialogs
from controllers.categories.controller import CategoriesController
from controllers.AI.controller import AIChatController
from client.client import ClientStorage
from themes.themes import Theme


class CategoriesView:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.categories = []
        self.selected_card = None
        self.client_storage = ClientStorage(self.page)
        self.ai_controller = AIChatController()
        self.controller = CategoriesController()

    def deactivate_categories(self, category_id):
        self.controller.deactivate_category(category_id)
        self._load_categories()
        self._load_subcategories()

    def activate_categories(self, category_id):
        self.controller.activate_category(category_id)
        self._load_categories()
        self._load_subcategories()

    def deactivate_subcategories(self, subcategory_id):
        self.controller.deactivate_subcategory(subcategory_id)
        self._load_subcategories()

    def activate_subcategories(self, subcategory_id):
        self.controller.activate_subcategory(subcategory_id)
        self._load_subcategories()

    def _on_category_card_selected(self, card, e):
        if self.selected_card is not None:
            self.selected_card.deselect()
        self.selected_card = card
        self._load_subcategories()

    def _load_categories(self):
        self.categories = self.controller.fetch_all_categories()
        category_cards = []
        self.categories_container.content = ft.Column([])
        # self.selected_card = None  # Resetear selección
        for category in self.categories:
            category_id, name, description, is_active = category
            card = CategoryCard(
                self.theme,
                self.page,
                category_id,
                name,
                description,
                is_active,
                on_selected=self._on_category_card_selected,
                on_deactivate=self.deactivate_categories,
                on_activate=self.activate_categories).build()
            category_cards.append(card)

        self.categories_container.content = ft.Column(
            category_cards, scroll=ft.ScrollMode.AUTO, expand=True)
        self.page.update()

    def _load_subcategories(self):
        if self.selected_card:
            subcategories = self.controller.fetch_subcategories(
                self.selected_card.category_id)
            subcategory_cards = []
            self.subcategories_container.content = ft.Column([])
            for subcategory in subcategories:
                subcategory_id, category_id, name, description, is_active = subcategory
                card = SubcategoryCard(
                    self.theme,
                    self.page,
                    subcategory_id,
                    category_id,
                    name,
                    description,
                    is_active,
                    on_deactivate=self.deactivate_subcategories,
                    on_activate=self.activate_subcategories).build()
                subcategory_cards.append(card)

            self.subcategories_container.content = ft.Column(
                subcategory_cards, scroll=ft.ScrollMode.AUTO, expand=True)
            self.page.update()

    def _save_category(self, e):
        name = self.category_name_field.value.strip()
        description = self.category_description_field.value.strip()

        if self._check_if_exists_category(name):
            self.category_name_field.error_text = "Ya existe una categoría con ese nombre"
            self.page.update()
            return

        if not name:
            self.category_name_field.error_text = "El nombre no puede estar vacío"
            self.page.update()
            return
        else:
            self.category_name_field.error_text = ""

        self.controller.set_category(name, description)
        self.page.close(self.category_dialog)
        self._load_categories()

    def _save_subcategory(self, e):
        if self.selected_card is None:
            Dialogs.error_dialog(
                self.page, "Por favor, selecciona una categoría para agregar una subcategoría.")
            return

        name = self.category_name_field.value.strip()
        description = self.category_description_field.value.strip()

        if not name:
            self.category_name_field.error_text = "El nombre no puede estar vacío"
            self.page.update()
            return
        else:
            self.category_name_field.error_text = ""

        if self._check_if_exists_subcategory(self.selected_card.category_id, name):
            self.category_name_field.error_text = "Ya existe una subcategoría con ese nombre"
            self.page.update()
            return

        self.controller.set_subcategory(
            self.selected_card.category_id, name, description)
        self.page.close(self.category_dialog)
        self._load_subcategories()

    def _thinking_state(self, is_thinking: bool):
        if is_thinking:
            self.category_description_field.hint_text = "Pensando..."
            self.page.update()
        else:
            self.category_description_field.hint_text = ""
            self.page.update()

    def _check_if_exists_category(self, name: str) -> bool:
        categories = self.controller.fetch_all_categories()
        return any(category[1].lower() == name.lower() for category in categories)

    def _check_if_exists_subcategory(self, category_id: int, name: str) -> bool:
        subcategories = self.controller.fetch_subcategories(category_id)
        return any(subcategory[2].lower() == name.lower() for subcategory in subcategories)

    def _ai_generate_description(self, e):
        self.randomize_description_button.disabled = True
        category_name = self.category_name_field.value
        if category_name.strip() == "":
            self.category_description_field.hint_text = "Por favor, ingresa un nombre de categoría para generar una descripción."
            self.page.update()
            return
        self._thinking_state(True)
        response = self.ai_controller.generate_recommendations(
            category_name, self.client_storage.get_value("last_model") or "gemini-3.1-flash-lite-preview")
        self._thinking_state(False)
        self.category_description_field.value = response
        self.randomize_description_button.disabled = False
        self.page.update()

    def _create_dialog(self, title, name_label, description_label, on_save_callback, is_subcategory=False):
        self.category_name_field = ft.TextField(
            label=name_label,
            width=300,
            border_radius=20,
            border_color=self.theme.text_secondary
        )
        self.category_description_field = ft.TextField(
            label=description_label,
            width=300,
            border_radius=20,
            border_color=self.theme.text_secondary,
            multiline=True,
            min_lines=3,
            max_lines=5,
            hint_text="",
            on_focus=self._ai_generate_description
        )

        self.randomize_description_text = ft.Text(
            "Aleatoria", color=self.theme.text_secondary, size=12)
        self.randomize_description_button = ft.IconButton(
            icon=icons.SHUFFLE,
            icon_color=self.theme.text_primary,
            on_click=self._ai_generate_description,
            tooltip="Generar descripción aleatoria",
        )

        self.category_dialog = ft.AlertDialog(
            bgcolor=self.theme.bg,
            title=ft.Text(title),
            content=ft.Column([
                self.category_name_field,
                self.category_description_field,
                ft.Row(
                    [
                        self.randomize_description_button,
                        self.randomize_description_text,
                    ],
                    alignment=ft.MainAxisAlignment.START
                )
            ]),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(
                    self.category_dialog)),
                ft.TextButton("Crear", on_click=on_save_callback)
            ]
        )
        self.page.open(self.category_dialog)
        self.page.update()

    def _open_create_subcategory_dialog(self, e):
        if self.selected_card is None:
            Dialogs.error_dialog(
                self.page, "Por favor, selecciona una categoría para agregar una subcategoría.")
            return
        self._create_dialog(
            title=f"Crear Subcategoría para {self.selected_card.name}",
            name_label="Nombre de Subcategoría",
            description_label="Descripción",
            on_save_callback=self._save_subcategory,  # Puede ser diferente si lo necesitas
            is_subcategory=True
        )

    def _open_create_category_dialog(self, e):
        self._create_dialog(
            title="Crear Categoría",
            name_label="Nombre",
            description_label="Descripción",
            on_save_callback=self._save_category,
            is_subcategory=False
        )

    def draw(self, header: Header):
        self.header = header.create("Categorías", return_page=True)

        self.add_category_button = ft.Row(
            [
                ft.Text("Agregar Categoria", color=self.theme.text_primary),
                ft.IconButton(
                    icon=icons.ADD,
                    on_click=self._open_create_category_dialog,
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        self.add_subcategory_button = ft.Row(
            [
                ft.Text("Agregar Subcategoria", color=self.theme.text_primary),
                ft.IconButton(
                    icon=icons.ADD,
                    on_click=self._open_create_subcategory_dialog,
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        self.categories_container = ft.Container(
            ft.Column(
                []
            ),
            border=ft.border.all(1, self.theme.text_secondary),
            border_radius=10,
            expand=True
        )

        self.subcategories_container = ft.Container(
            ft.Column(
                []
            ),
            border=ft.border.all(1, self.theme.text_secondary),
            border_radius=10,
            expand=True
        )

        self._load_categories()

        return ft.Container(
            ft.Column([
                self.header,
                self.add_category_button,
                self.categories_container,
                self.add_subcategory_button,
                self.subcategories_container
            ], expand=True),
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
            expand=True,
        )


class CategoryCard():
    def __init__(self, theme, page, category_id, name, description, is_active, on_selected=None, on_delete=None, on_deactivate=None, on_activate=None):
        self.theme = theme
        self.page = page
        self.category_id = category_id
        self.name = name
        self.description = description
        self.is_active = is_active

        # Self Properties
        self.is_selected = False
        self.is_disabled = False
        self.opacity = 1.0 if self.is_active else 0.5
        self.icon = icons.VISIBILITY if self.is_active else icons.VISIBILITY_OFF
        self.function = self.deactivate if self.is_active else self.activate

        # Callbacks
        self.on_selected = on_selected
        self.on_delete = on_delete
        self.on_deactivate = on_deactivate
        self.on_activate = on_activate

        self.card = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(name, weight=ft.FontWeight.BOLD, size=16),
                    ft.Text(description, size=14,
                            color=self.theme.text_secondary),
                ], expand=True, disabled=self.is_disabled, opacity=self.opacity),

                ft.Column([
                    ft.IconButton(
                        icon=self.icon,
                        icon_color=self.theme.text_primary,
                        on_click=self.function,
                        mouse_cursor=ft.MouseCursor.GRAB
                    )
                ]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand=True),
            margin=ft.margin.symmetric(vertical=10, horizontal=10),
            expand=True,
            bgcolor=self.theme.bg,
            data={"category_id": category_id},
            on_click=self._on_card_click,
        )

    def _on_card_click(self, e):
        if not self.is_selected:
            self.select()
            if self.on_selected:
                self.on_selected(self, e)

    def select(self):
        self.is_selected = True
        self.card.bgcolor = self.theme.fg
        self.page.update()

    def deselect(self):
        self.is_selected = False
        self.card.bgcolor = self.theme.bg
        self.page.update()

    def activate(self, e):
        if not self.is_active:
            self.on_activate(self.category_id)
            if self.is_disabled:
                self.is_disabled = False

    def deactivate(self, e):
        if self.on_deactivate:
            self.on_deactivate(self.category_id)
            if not self.is_disabled:
                self.is_disabled = True

    def build(self):
        return self.card


class SubcategoryCard(CategoryCard):
    def __init__(self, theme, page, subcategory_id, category_id, name, description, is_active, on_selected=None, on_delete=None, on_deactivate=None, on_activate=None):
        super().__init__(theme, page, category_id, name, description,
                         is_active, on_selected, on_delete, on_deactivate, on_activate)

        self.subcategory_id = subcategory_id

    def deactivate(self, e):
        if self.on_deactivate:
            self.on_deactivate(self.subcategory_id)
            if not self.is_disabled:
                self.is_disabled = True

    def activate(self, e):
        if not self.is_active:
            self.on_activate(self.subcategory_id)
            if self.is_disabled:
                self.is_disabled = False

    def select(self):
        pass

    def _on_card_click(self, e):
        pass

    def deselect(self):
        pass
