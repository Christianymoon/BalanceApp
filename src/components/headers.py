from themes.themes import Theme
import flet as ft
from flet import Icons as icons
from controllers.controller import UserDataController


class HeaderSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.page.overlay.clear()

    def _open_notification_panel(self, e):
        state = e.control.data
        if not state:
            # Obtener notificaciones
            notifications = self.page.notification_manager.get_all(
            ) if hasattr(self.page, 'notification_manager') else []

            # Construir elementos de notificación
            notification_items = []
            if notifications:
                for notification in notifications:
                    notification_item = ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(notification.title, color=self.theme.text_primary,
                                        size=12, weight=ft.FontWeight.W_500),
                                ft.Text(
                                    notification.message, color=self.theme.text_secondary, size=10, max_lines=2),
                                ft.Text(notification.created_at,
                                        color=self.theme.text_secondary, size=8),
                            ], spacing=2, expand=True),
                        ]),
                        padding=ft.padding.all(12),
                        bgcolor=self.theme.fg,
                        margin=ft.margin.symmetric(horizontal=0, vertical=4),
                    )
                    notification_items.append(notification_item)
            else:
                notification_items = [
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(icons.NOTIFICATIONS_NONE,
                                    color=self.theme.text_secondary, size=24),
                            ft.Text("No hay notificaciones",
                                    color=self.theme.text_secondary, size=11),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                        alignment=ft.alignment.center,
                        padding=ft.padding.all(24),
                    )
                ]

            panel_content = ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            notification_items,
                            scroll=ft.ScrollMode.AUTO,
                            expand=True,
                            spacing=0,
                        ),
                        width=300,
                        expand=True,
                        bgcolor=self.theme.fg,
                        padding=ft.padding.symmetric(
                            horizontal=12, vertical=12),
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
            )

            self.page.overlay.append(panel_content)
            e.control.data = True
        else:
            self.page.overlay.clear()
            e.control.data = False
        self.page.update()

    def create(self, placeholder="Bienvenido de nuevo", return_page=True, config=False):

        self.userdata = UserDataController.controller_fetch_userdata()

        self.header_container = ft.Row(
            expand=True,
        )

        self.retrun_button = ft.IconButton(
            icons.ARROW_BACK_IOS,
            icon_color=self.theme.text_primary,
            icon_size=20,
            on_click=lambda e: self.page.go("/"),
            expand=True,
            bgcolor=self.theme.fg,
        )

        self.placeholder = ft.Text(
            placeholder,
            color=self.theme.text_primary,
            size=18,
            weight=ft.FontWeight.W_500,
            expand=True,
        )

        self.placeholder_container = ft.Container(
            content=self.placeholder,
            expand=True,
            alignment=ft.alignment.center,
        )

        self.return_button_container = ft.Container(
            content=self.retrun_button,
        )

        # self.notification_button = ft.IconButton(icons.NOTIFICATIONS, icon_color=self.theme.text_secondary, icon_size=20, on_click=self._open_notification_panel, data=False)

        self.settings_button = ft.IconButton(
            icons.SETTINGS, icon_color=self.theme.text_primary, icon_size=20, on_click=lambda e: self.page.go("/settings"))

        self.profile_image = ft.Image(
            "./assets/avatar/profile.png", fit=ft.ImageFit.COVER, width=45, height=45)

        self.profile_container = ft.Container(
            content=self.profile_image,
            width=45,
            height=45,
            border_radius=ft.border_radius.all(40),
            on_click=lambda e: self.page.go("/user"),
        )

        self.header_container.controls.append(self.placeholder_container)

        if return_page:
            self.header_container.controls.insert(
                0, self.return_button_container)
        else:
            if self.page.client_storage.get("christianymoon.finance.profile_pic"):
                self.profile_image.src = self.page.client_storage.get(
                    "christianymoon.finance.profile_pic")
            else:
                self.profile_image.src = "./assets/avatar/profile.png"

            if self.userdata[2] == "Femenino":
                self.placeholder.value = f"Bienvenida de nuevo, {self.userdata[1]}!"
            elif self.userdata[2] == "Masculino":
                self.placeholder.value = f"Bienvenido de nuevo, {self.userdata[1]}!"

            self.header_container.controls.insert(0, self.profile_container)

        if config:
            self.header_container.controls.append(self.settings_button)
            # self.header_container.controls.append(self.notification_button)

        return ft.Container(
            self.header_container,
            bgcolor=self.theme.bg,
            margin=ft.margin.only(top=20),
        )
