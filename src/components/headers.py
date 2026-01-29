from themes.themes import Theme
import flet as ft 
from flet import Icons as icons
from controllers.controller import UserDataController

class HeaderSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.header = None
        self.file_picker = ft.FilePicker(
            on_result=self.change_background,

        )
        self.page.overlay.append(self.file_picker)

    def change_background(self, e):
        if e.files:
            file = e.files[0]
            img_path = file.path
            self.page.client_storage.remove("christianymoon.finance.profile_pic")
            self.page.client_storage.set("christianymoon.finance.profile_pic", img_path)
            self.header.content.controls[0].content.src = self.page.client_storage.get("christianymoon.finance.profile_pic")
            self.page.update()

    def create(self, placeholder="Bienvenido de nuevo", return_page=True, config=False):
        self.header = ft.Container(
            content=ft.Row([
                ft.Text(placeholder, color=self.theme.text_primary,size=18, weight=ft.FontWeight.W_500, expand=True),
                # ft.Container(width=40, border=ft.border.all(1, "purple"),),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            margin=ft.margin.only(top=25),
            padding=ft.padding.symmetric(vertical=10),
            bgcolor=self.theme.bg
        )

        
        if config:
            self.header.content.controls.append(ft.IconButton(icons.SETTINGS, icon_color=self.theme.text_secondary, icon_size=20, on_click=lambda e: self.page.go("/settings")))

        if not return_page:
            # CREATE PROFILE PICTURE
            self.header.content.controls.insert(0,
                ft.Container(content=ft.Image("./assets/avatar/profile.png", fit=ft.ImageFit.COVER, width=45, height=45),
                            width=45,
                            height=45,
                            # border=ft.border.all(1, "purple"),
                            # padding=4,
                            border_radius=ft.border_radius.all(40),
                            on_click=self.file_picker.pick_files)
                )
            
            # CHANGE PIC IF USER PICK IMAGE
            if self.page.client_storage.contains_key("christianymoon.finance.profile_pic"):
                self.header.content.controls[0].content.src = self.page.client_storage.get("christianymoon.finance.profile_pic")
                self.page.update()

            self.header.padding = ft.padding.symmetric(horizontal=20, vertical=10)
            self.userdata = UserDataController.controller_fetch_userdata()
            if self.userdata[2] == "Femenino":
                self.header.content.controls[1].value = f"Bienvenida de nuevo, {self.userdata[1]}!"
            elif self.userdata[2] == "Masculino":
                self.header.content.controls[1].value = f"Bienvenido de nuevo, {self.userdata[1]}!"

        if return_page:
            self.header.content.controls.insert(0,
                                           ft.IconButton(
                                               icon=icons.ARROW_BACK_IOS,
                                               icon_color=self.theme.text_primary,
                                               icon_size=20,
                                               on_click=lambda e: self.page.go(
                                                   "/")
                                           )
                                           )

        return self.header