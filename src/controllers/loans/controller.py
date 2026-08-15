from datetime import datetime
import logging

from controllers.actives.controller import ActiveController
from controllers.passives.controller import PassiveController
from db.database import Database


class LoanController:
    def __init__(self):
        pass

    @staticmethod
    def calculate_interest(amount, interest):
        try:
            total_interest = float(amount) * (float(interest) / 100)
            return total_interest
        except Exception as e:
            logging.error(
                f"Error during calculate interest {e}", exc_info=True)
            return 0.0

    def paid(id):
        db = Database()
        try:
            db.paid_loan(id)
        except Exception as e:
            logging.error(f"Error during set paid {e}", exc_info=True)
            raise e

    def controller_fetch_loans():
        db = Database()
        try:
            loans = db.fetch_borrowings()
            return loans
        except Exception as e:
            logging.error(f"Error during fetch loans: {e}", exc_info=True)
            return []

    def liquidate(id, loan_active_id, pay_account_id):
        db = Database()
        try:
            loan = LoanController.fetch(id)
            LoanController.paid(id)
            ActiveController.controller_update_active(
                pay_account_id, float(loan[3]), True)
            ActiveController.controller_delete_active(loan_active_id)
        except Exception as e:
            logging.error(f"Error during liquidate loan: {e}", exc_info=True)
            raise e

    def delete(id):
        db = Database()
        try:
            db.delete_borrowing(id)
        except Exception as e:
            logging.error(f"Error during delete loan: {e}", exc_info=True)

    def fetch(id):
        db = Database()
        try:
            return db.fetch_one_borrowing(id)
        except Exception as e:
            logging.error(f"Error during fetch loan: {e}", exc_info=True)
            return []

    def set(name, amount, interest, _id, to, _from):
        db = Database()
        if _from == "bank":
            PassiveController.controller_set_passive(
                name, "Prestamo", float(amount), False)
            active_id = ActiveController.controller_set_active(
                name, "Prestamo", float(amount), False)
            total_payment = LoanController.calculate_interest(
                amount, interest) + float(amount)
            created_at = datetime.now().astimezone().strftime("%d/%m/%Y %H:%M")
            db.set_borrowing(active_id, name, amount,
                             interest, total_payment, created_at)
            return
        try:
            account = ActiveController.controller_fetch_active(_id)
            if account[3] < float(amount):
                raise Exception("No hay suficiente saldo en la cuenta")

            if account and account[4]:
                ActiveController.controller_update_active(
                    _id, float(amount), False)  # Baja liquidez
                active_id = ActiveController.controller_set_active(
                    # Crea activo no liquido
                    name, "Prestamo", float(amount), False)
                total_payment = LoanController.calculate_interest(
                    amount, interest) + float(amount)
                created_at = datetime.now().astimezone().strftime("%d/%m/%Y %H:%M")
                db.set_borrowing(active_id, name, amount,
                                 interest, total_payment, created_at)
        except Exception as e:
            logging.error(f"Error during set loan {e}", exc_info=True)
            raise e
