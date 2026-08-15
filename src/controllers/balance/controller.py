from datetime import date

from db.database import Database


class BalanceController:
    @staticmethod
    def controller_set_balance(amount, new=False):
        db = Database()
        if new:
            db.set_balance(amount)
            return

        db.update_atomic_balance(amount)

    @staticmethod
    def controller_fetch_balance(formated=False):
        db = Database()
        try:
            balance = db.fetch_balance()[1]
        except TypeError:
            db.set_balance(0.0)
            balance = db.fetch_balance()[1]

        if formated:
            return f"${balance:,.2f}"
        return balance

    @staticmethod
    def controller_change_balance(amount, is_income):
        if not is_income:
            amount = -float(amount)
        else:
            amount = float(amount)

        BalanceController.controller_set_balance(amount)  # updates now only

    def fetch_balance_update():
        db = Database()
        return db.fetch_balance()[2]

    @staticmethod
    def fetch_snapshots():
        db = Database()
        return db.fetch_balance_snapshots()

    @staticmethod
    def fetch_last_date_snapshot():
        db = Database()
        return db.fetch_last_date_snapshot()

    @classmethod
    def make_snapshot(cls):
        db = Database()
        last_snapshot_date = db.fetch_last_date_snapshot()
        if (last_snapshot_date != date.today().isoformat()) or (last_snapshot_date == None):
            db.make_snapshot(cls.controller_fetch_balance(
                formated=False), date.today().isoformat())
