from datetime import date, datetime, timedelta
import logging

import flet as ft

from themes.themes import Theme


def get_group_date(date: date, timelapse: str):
    try:

        if isinstance(date, str) and date:
            date = datetime.strptime(date, "%d/%m/%Y %H:%M").date()
        else:
            date = date.date()

        if timelapse == "week":
            week_start = date - timedelta(days=date.weekday())
            return week_start

        if timelapse == "month":
            return date.year, date.month

        if timelapse == "year":
            return date.year

    except Exception as e:
        logging.error(f"Error al obtener la fecha: {e}")


def create_week_separator(week_start: date, theme: Theme):
    months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
              "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    week_end = week_start + timedelta(days=6)

    start_str = f"{months[week_start.month - 1]} {week_start.day}"
    end_str = f"{months[week_end.month - 1]} {week_end.day}"

    return ft.Container(
        content=ft.Text(
            f"Semana del {start_str} al {end_str}",
            color=theme.text_primary,
            size=14,
            weight=ft.FontWeight.W_500
        ),
        padding=ft.padding.only(top=10),
        expand=True
    )


def create_month_separator(month: date, year: date, theme: Theme):
    months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
              "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    return ft.Text(
        f"{months[month - 1]} {year}",
        color=theme.text_primary,
        size=14,
        weight=ft.FontWeight.W_500
    )
