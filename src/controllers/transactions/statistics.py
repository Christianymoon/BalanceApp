from db.database import Database
from dto.transactions import TransactionFilterDTO


def fetch_summary(filter: TransactionFilterDTO, formated=True):
    db = Database()
    summary = db.fetch_summary(filter)
    total = summary[0] if summary and summary[0] is not None else 0.0
    if formated:
        return f"${total:,.2f}"
    return total
