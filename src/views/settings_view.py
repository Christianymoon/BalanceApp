import logging
import os

import flet as ft
from flet import Icons as icons

from client.client import ClientStorage
from core.config import FLET_APP_STORAGE_DATA
from setup import log_dir
from themes.themes import Theme


class Settings:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.client = ClientStorage(self.page)
        self.in_out_mode_value = self.client.get_value("in_out_mode_setting")

    def handle_in_out_mode(self, e):
        try:
            old_value = self.client.get_value("in_out_mode_setting")
            self.client.set_value("in_out_mode_setting", not old_value)
            self.in_out_mode_value = self.client.get_value(
                "in_out_mode_setting")
        except Exception as error:
            logging.error(
                f"Error during change in out mode: {error}", exc_info=True)

        self.page.update()

    def handle_theme(self, e):
        new_value = e.control.value
        self.client.set_value("dark_mode", new_value)
        logging.info(f"Dark Mode changed to status {new_value}")

        dialog = ft.CupertinoAlertDialog(
            title=ft.Text("Reinicie la aplicación"),
            content=ft.Text("Reinicie la aplicación para aplicar los cambios"),
            actions=[
                ft.CupertinoDialogAction(
                    "Ok",
                    is_default_action=True,
                    on_click=lambda e: self.page.close(dialog)
                )
            ]
        )
        self.page.open(dialog)

    def copy_to_clipboard(self, text, name):
        self.page.set_clipboard(text)
        self.page.open(
            ft.SnackBar(
                content=ft.Text(f"{name} copiada al portapapeles"),
                action="Ok"
            )
        )

    def _get_opacity_color(self, color_str: str, opacity: float = 0.12) -> str:
        alpha_hex = f"{int(opacity * 255):02x}"
        if color_str.startswith("#"):
            hex_val = color_str.lstrip("#")
            if len(hex_val) == 6:
                return f"#{alpha_hex}{hex_val}"
            elif len(hex_val) == 8:
                return f"#{alpha_hex}{hex_val[2:]}"
        return color_str

    def _create_setting_card(self, title: str, subtitle: str, icon: str, icon_color: str, bg_opacity_color: str, trailing_control: ft.Control = None, on_click=None):
        controls = [
            ft.Container(
                content=ft.Icon(icon, color=icon_color, size=20),
                bgcolor=bg_opacity_color,
                width=38,
                height=38,
                border_radius=8,
                alignment=ft.alignment.center,
            ),
            ft.VerticalDivider(width=10, color="transparent"),
            ft.Column(
                [
                    ft.Text(title, color=self.theme.text_primary,
                            weight=ft.FontWeight.W_600, size=14),
                    ft.Text(subtitle, color=self.theme.text_secondary,
                            size=11, max_lines=2),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=2,
                expand=True,
            )
        ]
        if trailing_control:
            controls.append(trailing_control)
        elif on_click:
            controls.append(ft.Icon(icons.CHEVRON_RIGHT,
                            color=self.theme.text_secondary, size=20))

        return ft.Container(
            content=ft.Row(
                controls,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=self.theme.fg,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_radius=12,
            on_click=on_click,
        )

    def draw(self, header):
        self.header = header.create("Configuración", return_page=True)

        # Switches
        self.in_out_mode_switch = ft.CupertinoSwitch(
            value=self.in_out_mode_value,
            scale=0.6,
            key="in_out_mode",
            on_change=self.handle_in_out_mode,
        )

        self.change_theme_switch = ft.CupertinoSwitch(
            value=self.client.get_value("dark_mode"),
            scale=0.6,
            key="dark_mode",
            on_change=self.handle_theme
        )

        # Paths display
        db_path = os.path.join(FLET_APP_STORAGE_DATA or "", "financeapp.db")
        db_path_display = db_path
        if len(db_path_display) > 35:
            db_path_display = "..." + db_path_display[-32:]

        log_path_display = log_dir
        if len(log_path_display) > 35:
            log_path_display = "..." + log_path_display[-32:]

        # Settings list
        settings_column = ft.Column(
            [
                ft.Text("PREFERENCIAS", size=11,
                        weight=ft.FontWeight.BOLD, color=self.theme.blue_color),
                self._create_setting_card(
                    "Modo Oscuro",
                    "Cambiar el tema visual de la aplicación.",
                    icons.BRIGHTNESS_4,
                    self.theme.text_secondary,
                    self._get_opacity_color(self.theme.text_secondary, 0.12),
                    self.change_theme_switch
                ),
                self._create_setting_card(
                    "Modo solo transacciones",
                    "Oculta secciones de préstamos, activos y pasivos.",
                    icons.RECEIPT_LONG,
                    self.theme.text_secondary,
                    self._get_opacity_color(self.theme.text_secondary, 0.12),
                    self.in_out_mode_switch
                ),

                ft.Container(height=10),  # Spacer
                ft.Text("DATOS Y ORGANIZACIÓN", size=11,
                        weight=ft.FontWeight.BOLD, color=self.theme.blue_color),
                self._create_setting_card(
                    "Gestionar Categorías",
                    "Administrar categorías y subcategorías.",
                    icons.CATEGORY_OUTLINED,
                    self.theme.text_secondary,
                    self._get_opacity_color(self.theme.text_secondary, 0.12),
                    on_click=lambda e: self.page.go("/categories")
                ),
                self._create_setting_card(
                    "Acciones de Base de Datos",
                    "Mantenimiento y reestablecimiento de datos.",
                    icons.STORAGE_OUTLINED,
                    self.theme.text_secondary,
                    self._get_opacity_color(self.theme.text_secondary, 0.12),
                    on_click=lambda e: self.page.go("/databaseactions")
                ),

                ft.Container(height=10),  # Spacer
                ft.Text("INFORMACIÓN DEL SISTEMA", size=11,
                        weight=ft.FontWeight.BOLD, color=self.theme.blue_color),
                self._create_setting_card(
                    "Base de Datos",
                    db_path_display,
                    icons.DATA_OBJECT,
                    self.theme.text_secondary,
                    self._get_opacity_color(self.theme.text_secondary, 0.12),
                    on_click=lambda e: self.copy_to_clipboard(
                        db_path, "Ruta de la base de datos")
                ),
                self._create_setting_card(
                    "Archivo de Registro (Logs)",
                    log_path_display,
                    icons.INSERT_DRIVE_FILE_OUTLINED,
                    self.theme.text_secondary,
                    self._get_opacity_color(self.theme.text_secondary, 0.12),
                    on_click=lambda e: self.copy_to_clipboard(
                        log_dir, "Ruta de logs")
                ),
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        return ft.Container(
            ft.Column([
                self.header,
                ft.Container(height=15),
                settings_column
            ], expand=True),
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
            expand=True,
        )
