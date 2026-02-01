from themes.themes import Theme
import flet as ft 
from flet import Icons as icons
from controllers.controller import UserDataController

class HeaderSection:
    def __init__(self, theme: Theme, page: ft.Page):
        self.theme = theme
        self.page = page
        self.page.overlay.clear()
        self.file_picker = ft.FilePicker(
            on_result=self.change_profile_pic,

        )

        
        
    def change_profile_pic(self, e):
        if e.files:
            file = e.files[0]
            img_path = file.path
            self.page.client_storage.remove("christianymoon.finance.profile_pic")
            self.page.client_storage.set("christianymoon.finance.profile_pic", img_path)
            self.profile_image.src = self.page.client_storage.get("christianymoon.finance.profile_pic")
            self.page.update()

    def create(self, placeholder="Bienvenido de nuevo", return_page=True, config=False):

        self.userdata = UserDataController.controller_fetch_userdata()

        self.header_container = ft.Row(
            expand=True, 
        )

        self.retrun_button = ft.IconButton(
            icons.ARROW_BACK_IOS, 
            icon_color=self.theme.text_secondary, 
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

        self.settings_button = ft.IconButton(icons.SETTINGS, icon_color=self.theme.text_secondary, icon_size=20, on_click=lambda e: self.page.go("/settings"))

        self.profile_image = ft.Image("./assets/avatar/profile.png", fit=ft.ImageFit.COVER, width=45, height=45)

        self.profile_container = ft.Container(
            content=self.profile_image,
            width=45,
            height=45,
            border_radius=ft.border_radius.all(40),
            on_click=self.file_picker.pick_files)

        self.header_container.controls.append(self.placeholder_container)

        if return_page:
            self.header_container.controls.insert(0, self.return_button_container)
        else:
            self.page.overlay.append(self.file_picker)
            if self.page.client_storage.get("christianymoon.finance.profile_pic"):
                self.profile_image.src = self.page.client_storage.get("christianymoon.finance.profile_pic")
            else:
                self.profile_image.src = "./assets/avatar/profile.png"
            
            if self.userdata[2] == "Femenino":
                self.placeholder.value = f"Bienvenida de nuevo, {self.userdata[1]}!"
            elif self.userdata[2] == "Masculino":
                self.placeholder.value = f"Bienvenido de nuevo, {self.userdata[1]}!"
            
            self.header_container.controls.insert(0, self.profile_container)

        if config:
            self.header_container.controls.append(self.settings_button)

        return ft.Container(
            self.header_container,
            bgcolor=self.theme.bg,
            padding=ft.padding.symmetric(horizontal=20),
            margin=ft.margin.only(top=20),
        )