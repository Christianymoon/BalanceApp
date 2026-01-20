import flet as ft 

class LoanView:
    def __init__(self, page: ft.Page, theme):
        self.page = page
        self.theme = theme

    def create(self):
        return ft.Column([
            ft.Text("Loan View")
        ])