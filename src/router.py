import logging

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
from views.ai_chat_view import AIChatView
from views.all_transactions_view import AllTransactionsView
from views.categories_view import CategoriesView
from views.databaseactions_view import DatabaseActionsView
from views.user_view import UserView

from components.headers import HeaderSection
from themes.themes import Theme


views = {
    "/": MainSection,
    "/transaction": TransactionSection,
    "/balance": BalanceSection,
    "/active": ActiveSection,
    "/passive": PassiveSection,
    "/passive_item": PassiveItemView,
    "/borrows": BorrowSection,
    "/loan": LoanView,
    "/settings": Settings,
    "/error": ErrorPage,
    "/setup": Setup,
    "/intertransfer": IntertransferView,
    "/ai_chat": AIChatView,
    "/all_transactions": AllTransactionsView,
    "/categories": CategoriesView,
    "/databaseactions": DatabaseActionsView,
    "/user": UserView,
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
        import traceback
        import platform
        import os
        from datetime import datetime

        # Safe imports to prevent circular references
        try:
            from core.config import FLET_APP_STORAGE_DATA
            db_path = os.path.join(
                FLET_APP_STORAGE_DATA or "", "financeapp.db")
        except Exception:
            db_path = "financeapp.db"

        try:
            from setup import log_dir
        except ImportError:
            log_dir = "./applogs.log"

        tb_str = "".join(traceback.format_exception(
            type(e), e, e.__traceback__))
        flet_ver = getattr(ft, "__version__", "Desconocida")

        report_text = (
            f"--- REPORTE DE SOPORTE ---\n"
            f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Ruta Fallida: {route}\n"
            f"Error: {type(e).__name__}: {str(e)}\n"
            f"SO: {platform.system()} {platform.release()} ({platform.machine()})\n"
            f"Python: {platform.python_version()}\n"
            f"Flet: {flet_ver}\n"
            f"Resolución: {page.width}x{page.height}\n"
            f"Base de Datos: {db_path}\n"
            f"Archivo Logs: {log_dir}\n"
            f"\n--- TRACEBACK ---\n"
            f"{tb_str}"
        )

        def copy_report(ev):
            page.set_clipboard(report_text)
            page.open(
                ft.SnackBar(
                    content=ft.Text(
                        "Reporte de soporte copiado al portapapeles.", color="#FFFFFF"),
                    bgcolor=theme.green_color,
                    action="Ok"
                )
            )
            page.update()

        error_details = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.BUG_REPORT,
                            color=theme.red_color, size=24),
                    ft.Text(type(e).__name__, size=16,
                            weight=ft.FontWeight.BOLD, color=theme.red_color),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Text(str(e), size=14, color=theme.text_primary,
                        selectable=True),
            ], spacing=8),
            bgcolor=theme.fg,
            padding=16,
            border_radius=12,
            border=ft.border.all(1, theme.red_color),
        )

        info_items = [
            ("Fecha y Hora", datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ("Ruta Fallida", route),
            ("Sistema Operativo", f"{platform.system()} {platform.release()}"),
            ("Versión Python", platform.python_version()),
            ("Resolución Pantalla", f"{page.width}x{page.height}"),
        ]

        info_rows = []
        for label, val in info_items:
            info_rows.append(
                ft.Row([
                    ft.Text(label, size=13, color=theme.text_secondary,
                            weight=ft.FontWeight.W_500),
                    ft.Text(val, size=13, color=theme.text_primary,
                            weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )

        info_box = ft.Container(
            content=ft.Column(info_rows, spacing=8),
            bgcolor=theme.fg,
            padding=16,
            border_radius=12,
        )

        traceback_box = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.TERMINAL,
                            color=theme.blue_color, size=18),
                    ft.Text("Traceback (Pila de llamadas)", size=13,
                            weight=ft.FontWeight.BOLD, color=theme.blue_color),
                ]),
                ft.Divider(height=1, color=theme.bg),
                ft.Container(
                    content=ft.Text(
                        tb_str,
                        font_family="monospace",
                        size=11,
                        color="#A8FFB2" if theme.bg == "#0D0E0D" else "#006600",
                        selectable=True,
                    ),
                    height=180,
                    # scroll=ft.ScrollMode.AUTO,
                )
            ], spacing=8),
            bgcolor="#1A1C1A" if theme.bg == "#0D0E0D" else "#F0F0F0",
            padding=16,
            border_radius=12,
            border=ft.border.all(1, theme.fg),
        )

        main_column = ft.Column(
            [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.REPORT_PROBLEM,
                                color=theme.red_color, size=64),
                        ft.Text("¡Ups! Algo salió mal", size=24,
                                weight=ft.FontWeight.W_800, color=theme.text_primary),
                        ft.Text(
                            "La aplicación ha encontrado un error inesperado. A continuación se muestran los detalles técnicos para soporte.",
                            size=14, color=theme.text_secondary, text_align=ft.TextAlign.CENTER
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=20),
                ),

                ft.Text("DETALLES DEL ERROR", size=11,
                        weight=ft.FontWeight.BOLD, color=theme.blue_color),
                error_details,
                ft.Container(height=10),

                ft.Text("INFORMACIÓN DE SOPORTE", size=11,
                        weight=ft.FontWeight.BOLD, color=theme.blue_color),
                info_box,
                ft.Container(height=10),

                ft.Text("DIAGNÓSTICO TÉCNICO", size=11,
                        weight=ft.FontWeight.BOLD, color=theme.blue_color),
                traceback_box,
                ft.Container(height=20),

                ft.Row([
                    ft.ElevatedButton(
                        "Copiar Reporte",
                        icon=ft.Icons.CONTENT_COPY,
                        bgcolor=theme.blue_color,
                        color="#FFFFFF",
                        on_click=copy_report,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        expand=True,
                    ),
                    ft.OutlinedButton(
                        "Volver al Inicio",
                        icon=ft.Icons.HOME,
                        on_click=lambda _: page.go("/"),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            color=theme.text_primary,
                        ),
                        expand=True,
                    ),
                ], spacing=15),
            ],
            spacing=10,
        )

        page.views.clear()
        page.views.append(
            ft.View(
                route="/err",
                controls=[
                    ft.Container(
                        content=ft.Container(
                            content=main_column,
                        ),
                        alignment=ft.alignment.top_center,
                        padding=20,
                    )
                ],
                bgcolor=theme.bg,
                scroll=ft.ScrollMode.AUTO
            )
        )
        page.update()
