from controllers.controller import BalanceController
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from core.config import ASSETS_DIR


class ChartGenerator:
    def __init__(self):
        pass

    def balance_chart(self, days: list[datetime], balance: list[float]) -> str:
        if len(days) != len(balance):
            raise ValueError("Las fechas y los balances no coinciden")

        route = ASSETS_DIR + "/charts/balance_chart.png"

        plt.style.use("dark_background")

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(
            days,
            balance,
            linewidth=2.5,
            marker="o",
            markersize=5,
        )

        # Fondo
        fig.patch.set_facecolor("#000000")
        ax.set_facecolor("#000000")

        # Título y etiquetas
        ax.set_title("Evolución del Patrimonio", fontsize=16)
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Patrimonio")

        # Cuadrícula
        ax.grid(True, linestyle="--", alpha=0.25)

        # Mostrar todas las fechas
        ax.set_xticks(days)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))

        # Rotar etiquetas
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        # No cortar el primer y último punto
        ax.margins(x=0.03)

        # Ajustar límites del eje X
        ax.set_xlim(days[0], days[-1])

        fig.tight_layout()
        fig.savefig(route, dpi=200, bbox_inches="tight")
        plt.close(fig)

        return route
