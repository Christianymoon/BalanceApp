from db.database import Database
from dto.transactions import TransactionFilterDTO


def fetch_summary(filter: TransactionFilterDTO, formated=True):
    db = Database()
    summary = db.fetch_summary(filter)
    if formated:
        return f"${summary[0]:,.2f}"
    return summary[0]
