# from sqlalchemy import label
from themes.themes import Theme
from controllers.controller import UserDataController
from flet import Icons as icons
import flet as ft


DEFAULT_PROFILE_PIC = "./assets/avatar/profile.png"
PROFILE_PIC_KEY = "christianymoon.finance.profile_pic"


class UserView:
    """Vista de información del usuario.

    Por ahora muestra foto y nombre. El layout está pensado para
    ir agregando más secciones (género, preferencias, etc.) sin
    reestructurar el draw.
    """

    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.userdata = UserDataController.controller_fetch_userdata()
        self.file_picker = ft.FilePicker(on_result=self.change_profile_pic)

    def _get_username(self) -> str:
        if not self.userdata:
            return "Usuario"
        return self.userdata[1] or "Usuario"

    def _get_gender(self) -> str:
        if not self.userdata:
            return "No definido"
        return self.userdata[2] or "No definido"

    def _get_profile_pic_src(self) -> str:
        stored = self.page.client_storage.get(PROFILE_PIC_KEY)
        return stored if stored else DEFAULT_PROFILE_PIC

    def change_profile_pic(self, e):
        if not e.files:
            return

        img_path = e.files[0].path
        self.page.client_storage.remove(PROFILE_PIC_KEY)
        self.page.client_storage.set(PROFILE_PIC_KEY, img_path)
        self.profile_image.src = self.page.client_storage.get(PROFILE_PIC_KEY)
        self.page.update()

    def _open_file_picker(self, e):
        self.file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["jpg", "jpeg", "png", "webp", "gif"],
        )

    def _build_profile_header(self) -> ft.Control:
        """Bloque principal: foto + nombre. Click en la foto abre el file picker."""
        self.profile_image = ft.Image(
            src=self._get_profile_pic_src(),
            fit=ft.ImageFit.COVER,
            width=96,
            height=96,
        )

        avatar = ft.Container(
            content=ft.Stack(
                [
                    self.profile_image,
                    ft.Container(
                        content=ft.Icon(
                            icons.CAMERA_ALT,
                            color=self.theme.text_primary,
                            size=18,
                        ),
                        alignment=ft.alignment.bottom_right,
                        padding=ft.padding.only(right=4, bottom=4),
                    ),
                ],
                width=96,
                height=96,
            ),
            width=96,
            height=96,
            border_radius=ft.border_radius.all(48),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            bgcolor=self.theme.fg,
            alignment=ft.alignment.center,
            on_click=self._open_file_picker,
            tooltip="Cambiar foto de perfil",
        )

        self.username_text = ft.Text(
            self._get_username(),
            color=self.theme.text_primary,
            size=22,
            weight=ft.FontWeight.W_600,
            text_align=ft.TextAlign.CENTER,
        )

        change_photo_hint = ft.Text(
            "Toca la foto para cambiarla",
            color=self.theme.text_secondary,
            size=12,
            text_align=ft.TextAlign.CENTER,
        )

        return ft.Container(
            content=ft.Column(
                [
                    avatar,
                    ft.Container(height=12),
                    self.username_text,
                    ft.Container(height=4),
                    change_photo_hint,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=ft.padding.symmetric(vertical=24),
            alignment=ft.alignment.center,
            expand=False,
        )

    def _build_info_section(self) -> ft.Control:
        """Sección de datos del perfil.

        Punto de extensión: agregar filas con _info_row() a medida
        que se incorporen más campos del usuario.
        """
        rows = [
            self._info_row(
                icon=icons.PERSON_OUTLINE,
                label="Nombre",
                value=self._get_username(),
            ),
            self._info_row(
                icon=icons.MALE if self._get_gender() == "Masculino" else icons.FEMALE,
                label="Genero",
                value=self._get_gender(),
            )
            # Futuro: género, email, preferencias, etc.
            # self._info_row(icons.WC, "Género", gender),
        ]

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "INFORMACIÓN PERSONAL",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=self.theme.blue_color,
                    ),
                    ft.Container(height=4),
                    *rows,
                ],
                spacing=10,
            ),
            expand=False,
        )

    def _info_row(self, icon: str, label: str, value: str) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(
                            icon, color=self.theme.text_secondary, size=20),
                        bgcolor=self.theme.fg,
                        width=38,
                        height=38,
                        border_radius=8,
                        alignment=ft.alignment.center,
                    ),
                    ft.VerticalDivider(width=10, color="transparent"),
                    ft.Column(
                        [
                            ft.Text(
                                label,
                                color=self.theme.text_secondary,
                                size=11,
                            ),
                            ft.Text(
                                value,
                                color=self.theme.text_primary,
                                size=14,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=self.theme.fg,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_radius=12,
        )

    def draw(self, header):
        self.header = header.create("Perfil", return_page=True)
        self.page.overlay.append(self.file_picker)

        body = ft.Column(
            [
                self._build_profile_header(),
                self._build_info_section(),
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        return ft.Container(
            content=ft.Column(
                [
                    self.header,
                    ft.Container(height=10),
                    body,
                ],
                expand=True,
            ),
            margin=ft.margin.symmetric(horizontal=20, vertical=10),
            expand=True,
        )
