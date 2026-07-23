from enum import Enum
import flet as ft
from flet import Icons as icons
import threading

from themes.themes import Theme
from controllers.AI.controller import AIChatController
from client.client import ClientStorage


class KaraModels(Enum):
    GEMINI_3_5_FLASH = {"value": "Kara 3.5 Ultra", "key": "gemini-3.5-flash"}
    GEMINI_3_1_FLASH_LITE_PREVIEW = {
        "value": "Kara 3.1 Lite", "key": "gemini-3.1-flash-lite-preview"}
    GEMINI_2_5_FLASH = {"value": "Kara 2.5 Flash", "key": "gemini-2.5-flash"}


class KaraModelsThinkingPerformance(Enum):
    HIGH = {"value": "Ultra", "key": "high"}
    MEDIUM = {"value": "Normal", "key": "medium"}
    LOW = {"value": "Bajo", "key": "low"}
    MINIMAL = {"value": "Minimo", "key": "minimal"}


class AIChatView:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.messages_column: ft.Column = None
        self.prompt_field: ft.TextField = None
        self.send_button: ft.IconButton = None
        self._thinking_bubble = None
        self.client_storage = ClientStorage(self.page)
        self.aichat_controller = AIChatController()

    # ------------------------------------------------------------------ helpers

    def _bubble(self, text: str, is_user: bool) -> ft.Container:
        """Crea una burbuja de mensaje con estilo diferenciado."""
        if is_user:
            bg = self.theme.fg
            text_color = self.theme.text_primary
            border_color = self.theme.fg
            align = ft.MainAxisAlignment.END
            icon = icons.PERSON
            icon_color = self.theme.text_primary
        else:
            bg = self.theme.fg
            text_color = self.theme.text_primary
            border_color = self.theme.fg
            align = ft.MainAxisAlignment.START
            icon = icons.AUTO_AWESOME
            icon_color = self.theme.text_primary

        avatar = ft.Container(
            content=ft.Icon(icon, color=icon_color, size=16),
            width=30,
            height=30,
            bgcolor=bg,
            border_radius=15,
            alignment=ft.alignment.center,
            border=ft.border.all(1, border_color),
        )

        # Determinar el theme_mode local para que el Markdown pinte todo el texto correctamente
        bubble_theme_mode = ft.ThemeMode.LIGHT if self.theme.bg == "#FFFFFF" else ft.ThemeMode.DARK

        bubble = ft.Container(
            theme_mode=bubble_theme_mode,
            content=ft.Markdown(
                text,
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                code_theme=ft.MarkdownCodeTheme.ATOM_ONE_DARK,
                code_style_sheet=ft.MarkdownStyleSheet(
                    p_text_style=ft.TextStyle(color=text_color),
                    code_text_style=ft.TextStyle(
                        size=12, font_family="monospace"),
                ),
                on_tap_link=lambda e: self.page.launch_url(e.data),
            ),
            bgcolor=bg,
            border_radius=ft.border_radius.only(
                top_left=16, top_right=16,
                bottom_left=0 if is_user else 16,
                bottom_right=16 if is_user else 0,
            ),
            border=ft.border.all(1, border_color),
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
            expand=True,
        )

        controls = [avatar, bubble] if not is_user else [bubble, avatar]

        return ft.Container(
            content=ft.Row(controls, alignment=align, spacing=8, wrap=False),
            padding=ft.padding.symmetric(horizontal=16, vertical=4),
            expand=True,
        )

    def _thinking_indicator(self) -> ft.Container:
        """Burbuja animada de 'pensando...'."""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icons.AUTO_AWESOME,
                                    color=self.theme.text_primary, size=16),
                    width=30, height=30,
                    bgcolor=self.theme.fg,
                    border_radius=15,
                    alignment=ft.alignment.center,
                    border=ft.border.all(1, self.theme.fg),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.ProgressRing(width=14, height=14, stroke_width=2,
                                        color=self.theme.text_primary),
                        ft.Text("Analizando tus finanzas...",
                                color=self.theme.text_secondary, size=12,
                                italic=True),
                    ], spacing=8),
                    bgcolor=self.theme.fg,
                    border_radius=16,
                    border=ft.border.all(1, self.theme.fg),
                    padding=ft.padding.symmetric(horizontal=14, vertical=10),
                ),
            ], alignment=ft.MainAxisAlignment.START, spacing=8),
            padding=ft.padding.symmetric(horizontal=16, vertical=4),
        )

    def _add_message(self, text: str, is_user: bool):
        self.messages_column.controls.append(self._bubble(text, is_user))
        self.page.update()

    def _remove_thinking(self):
        if self._thinking_bubble and self._thinking_bubble in self.messages_column.controls:
            self.messages_column.controls.remove(self._thinking_bubble)
            self._thinking_bubble = None

    # ------------------------------------------------------------------ events

    def _on_send(self, e):
        prompt = self.prompt_field.value.strip()
        model = self.models_selection.value
        thinking_level = self.thinking_performance_selection.value
        # Guardar el modelo seleccionado
        self.client_storage.set_value("last_model", model)
        self.client_storage.set_value(
            "thinking_performance", thinking_level)

        if not prompt:
            return

        # Deshabilitar input mientras procesa
        self.prompt_field.value = ""
        self.prompt_field.disabled = True
        self.send_button.disabled = True
        self._add_message(prompt, is_user=True)

        # Mostrar indicador de carga
        self._thinking_bubble = self._thinking_indicator()
        self.messages_column.controls.append(self._thinking_bubble)
        self.page.update()

        # Llamar a la IA en hilo separado para no bloquear la UI
        def run_ai():
            response = self.aichat_controller.analyze_with_ai(
                prompt, model, thinking_level=thinking_level)
            self._remove_thinking()
            self._add_message(response, is_user=False)
            self.prompt_field.disabled = False
            self.send_button.disabled = False
            self.page.update()

        threading.Thread(target=run_ai, daemon=True).start()

    def _on_field_submit(self, e):
        self._on_send(e)

    # ------------------------------------------------------------------ draw

    def draw(self, header) -> ft.Column:
        # ---- Header
        header_bar = header.create("Kara AI", return_page=True)

        # ---- Banner informativo
        info_banner = ft.Container(
            content=ft.Row([
                ft.Icon(icons.INFO_OUTLINE,
                        color=self.theme.text_primary, size=16),
                ft.Text(
                    "Analiza tus últimas 100 transacciones con IA",
                    color=self.theme.text_secondary,
                    size=12,
                ),
            ], spacing=8),
            bgcolor=self.theme.fg,
            # border=ft.border.all(1, self.theme.text_primary),
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            margin=ft.margin.symmetric(horizontal=0, vertical=6),
        )

        # ---- Sugerencias de prompts rápidos
        suggestions = [
            "¿Cuáles son mis mayores gastos?",
            "¿Han cambiado mis hábitos de gasto?",
            "¿En qué categoría gasto más?",
            "Dame recomendaciones para ahorrar",
        ]

        self.models_selection = ft.Dropdown(
            options=[
                ft.dropdown.Option(
                    key=KaraModels.GEMINI_3_5_FLASH.value["key"], text=KaraModels.GEMINI_3_5_FLASH.value["value"]),
                ft.dropdown.Option(
                    key=KaraModels.GEMINI_3_1_FLASH_LITE_PREVIEW.value["key"], text=KaraModels.GEMINI_3_1_FLASH_LITE_PREVIEW.value["value"]),
                ft.dropdown.Option(
                    key=KaraModels.GEMINI_2_5_FLASH.value["key"], text=KaraModels.GEMINI_2_5_FLASH.value["value"]),
            ],
            value=self.client_storage.get_value(
                "last_model") or KaraModels.GEMINI_3_1_FLASH_LITE_PREVIEW.value["key"],
            expand=True,
            text_style=ft.TextStyle(color=self.theme.text_secondary, size=12),
            fill_color=self.theme.fg,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=1),
            dense=True,
            border_radius=20,
            border=ft.InputBorder.OUTLINE,
        )

        self.thinking_performance_selection = ft.Dropdown(
            options=[
                ft.dropdown.Option(leading_icon=icons.PSYCHOLOGY,
                                   key=KaraModelsThinkingPerformance.HIGH.value["key"], text=KaraModelsThinkingPerformance.HIGH.value["value"]),
                ft.dropdown.Option(leading_icon=icons.AUTO_AWESOME,
                                   key=KaraModelsThinkingPerformance.MEDIUM.value["key"], text=KaraModelsThinkingPerformance.MEDIUM.value["value"]),
                ft.dropdown.Option(leading_icon=icons.LIGHTBULB,
                                   key=KaraModelsThinkingPerformance.LOW.value["key"], text=KaraModelsThinkingPerformance.LOW.value["value"]),
                ft.dropdown.Option(leading_icon=icons.ENERGY_SAVINGS_LEAF,
                                   key=KaraModelsThinkingPerformance.MINIMAL.value["key"], text=KaraModelsThinkingPerformance.MINIMAL.value["value"]),
            ],
            value=self.client_storage.get_value(
                "thinking_performance") or KaraModelsThinkingPerformance.MINIMAL.value["key"],
            expand=True,
            text_style=ft.TextStyle(color=self.theme.text_secondary, size=12),
            fill_color=self.theme.fg,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=1),
            dense=True,
            border_radius=20,
            border=ft.InputBorder.OUTLINE,
        )

        models = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(
                        "Model", color=self.theme.text_secondary, size=12),
                    self.models_selection,
                ], expand=True),
                ft.Column([
                    ft.Text(
                        "Thinking Performance", color=self.theme.text_secondary, size=12),
                    self.thinking_performance_selection,
                ], expand=True),
            ]),
            margin=ft.margin.symmetric(horizontal=0, vertical=6),
        )

        def make_chip(text):
            return ft.Container(
                content=ft.Text(
                    text, color=self.theme.text_secondary, size=11),
                bgcolor=self.theme.fg,
                # border=ft.border.all(1, self.theme.text_primary),
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                on_click=lambda e, t=text: self._quick_send(t),
            )

        chips_row = ft.Container(
            content=ft.Row(
                [make_chip(s) for s in suggestions],
                scroll=ft.ScrollMode.AUTO,
                spacing=8,
            ),
            padding=ft.padding.symmetric(horizontal=0, vertical=4),
        )

        # ---- Área de mensajes
        welcome_msg = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(icons.AUTO_AWESOME,
                                    color=self.theme.text_primary, size=32),
                    width=60, height=60,
                    bgcolor=self.theme.bg,
                    border_radius=30,
                    alignment=ft.alignment.center
                ),
                ft.Text(
                    "¡Hola! Soy Kara tu asistente financiero.",
                    color=self.theme.text_primary,
                    size=14,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Text(
                    "Pregúntame sobre tus hábitos de gasto,\npatrones financieros o cómo mejorar tus finanzas.",
                    color=self.theme.text_secondary,
                    size=12,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=30),
        )

        self.messages_column = ft.Column(
            [welcome_msg],
            spacing=0,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            auto_scroll=True,
        )

        messages_area = ft.Container(
            content=self.messages_column,
            expand=True,
            bgcolor=self.theme.bg,
        )

        # ---- Input bar
        self.prompt_field = ft.TextField(
            hint_text="Escribe tu pregunta financiera...",
            hint_style=ft.TextStyle(color=self.theme.text_secondary),
            text_style=ft.TextStyle(color=self.theme.text_primary),
            border=ft.InputBorder.NONE,
            expand=True,
            cursor_color=self.theme.text_primary,
            multiline=False,
            on_submit=self._on_field_submit,
            max_lines=3,
        )

        self.send_button = ft.IconButton(
            icon=icons.SEND,
            icon_color=self.theme.text_primary,
            icon_size=22,
            on_click=self._on_send,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: self.theme.bg,
                         ft.ControlState.HOVERED: self.theme.fg},
                shape=ft.RoundedRectangleBorder(radius=20),
            ),
        )

        input_bar = ft.Container(
            content=ft.Row([
                self.prompt_field,
                self.send_button,
            ], alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6),
            bgcolor=self.theme.fg,
            border_radius=30,
            padding=ft.padding.symmetric(horizontal=12, vertical=4),
            margin=ft.margin.symmetric(horizontal=0, vertical=10),
        )

        return ft.Container(
            content=ft.Column([
                header_bar,
                info_banner,
                models,
                chips_row,
                messages_area,
                input_bar,
            ], expand=True, spacing=0),
            expand=True,
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
        )

    def _quick_send(self, text: str):
        self.prompt_field.value = text
        self.page.update()
        self._on_send(None)
