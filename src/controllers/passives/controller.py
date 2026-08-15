from datetime import datetime
import logging

from controllers.actives.controller import ActiveController
from controllers.balance.controller import BalanceController
from controllers.liquid.controller import LiquidController
from db.database import Database


class PassiveController:
    @staticmethod
    def controller_set_passive(name, category, amount, is_liquidated=False):
        db = Database()
        try:
            created_at = datetime.now().astimezone().strftime("%d/%m/%Y %H:%M")
            db.set_passive(name, category, amount, is_liquidated, created_at)
        except Exception as e:
            logging.error(f"Error during setting passive: {e}", exc_info=True)

        BalanceController.controller_change_balance(amount, False)

    @staticmethod
    def fetch_passive(id):
        db = Database()
        try:
            passive = db.fetch_passive(id)
            return passive
        except Exception as e:
            logging.error(f"Error during searching pasive on database: {e}")

    @staticmethod
    def pay_passive(id, active_id):

        db = Database()
        try:
            passive = PassiveController.fetch_passive(id)
            active = ActiveController.controller_fetch_active(active_id)
            if active[3] < passive[3]:
                raise ValueError(
                    "No tienes saldo suficiente para pagar este pasivo")
            if passive and not passive[4]:
                db.update_passive(id)
                db.update_active(active_id, active[3] - passive[3])
                LiquidController.change(passive[3], False)
        except Exception as e:
            logging.error(f"Error during paying passive: {e}", exc_info=True)
            raise e

    @staticmethod
    def controller_fetch_passives(order_by="price"):
        db = Database()
        try:
            all_passives = db.fetch_passives(order_by=order_by)
            return all_passives
        except Exception as e:
            logging.error(f"Error during fetch all passives: {e}")
            return []

    @staticmethod
    def controller_delete_passive(id):
        db = Database()
        try:
            db.delete_passive(id)
        except Exception as e:
            logging.error("Error during delete pasive {id} error: {e}")
