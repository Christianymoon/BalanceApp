import flet as ft

from views.main_view import MainSection
from views.transaction_view import TransactionSection
from views.balance_view import BalanceSection
from views.actives_view import ActiveSection
from views.passives_view import PassiveSection, PassiveItemView
from views.borrow_view import BorrowSection
from views.loan_view import LoanView
from views.settings_view import Settings
from views.error_view import ErrorPage
from views.setup_view import Setup
from views.intertransfer_view import IntertransferView

from components.headers import HeaderSection
from themes.themes import Theme

import logging


views = {
    "/" : MainSection,
    "/transaction" : TransactionSection,
    "/balance" : BalanceSection,
    "/active" : ActiveSection,
    "/passive" : PassiveSection,
    "/passive_item" : PassiveItemView,
    "/borrows" : BorrowSection,
    "/loan" : LoanView,
    "/settings" : Settings,
    "/error" : ErrorPage,
    "/setup" : Setup,
    "/intertransfer" : IntertransferView,
}



def navigate_to(page: ft.Page, theme: Theme, route: str):
    header = HeaderSection(theme, page)
    view = views[route](theme, page)

    try:
        page.views.clear()
        page.views.append(
            ft.View(
                route=route,
                controls=[
                    view.draw(header)
                ],
                bgcolor=theme.bg
            )
        )
        page.update()
    except Exception as e:
        logging.error(e)
        page.views.clear()
        page.views.append(
            ft.View(
                route="/err",
                controls=[
                    ft.Text("Error :( {}".format(e), size=24, weight=ft.FontWeight.BOLD, color=theme.text_primary),
                ],
                bgcolor=theme.bg
            )
        )
        page.update()