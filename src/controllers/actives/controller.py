from datetime import datetime
import logging

from controllers.balance.controller import BalanceController
from controllers.liquid.controller import LiquidController
from db.database import Database


class ActiveController:
    def __init__(self):
        pass

    @staticmethod
    def controller_set_active(name, active_type, amount, is_liquid):
        db = Database()
        try:
            active_id = db.set_active(active_type, name, amount, is_liquid)
        except Exception as e:
            logging.error(f"Error during set active {e}")

        if is_liquid:
            BalanceController.controller_change_balance(amount, True)
            LiquidController.change(amount, True)
        else:
            BalanceController.controller_change_balance(amount, True)

        return active_id

    @staticmethod
    def controller_fetch_actives():
        db = Database()
        try:
            all_actives = db.fetch_all_actives()
            return all_actives
        except Exception as e:
            logging.error(
                f"Error during fetching all actives: {e}", exc_info=True)
            return []

    @staticmethod
    def controller_fetch_active(id):
        db = Database()
        try:
            return db.fetch_active(id)
        except Exception as e:
            logging.error(f"Error during fetching active: {e}", exc_info=True)
            return []

    @staticmethod
    def set_price(id, price):
        db = Database()
        try:
            db.update_active(id, float(price))
            active = ActiveController.controller_fetch_active(id)
            if active[4]:
                BalanceController.controller_change_balance(float(price), True)
                LiquidController.change(float(price), True)
            else:
                BalanceController.controller_change_balance(float(price), True)
        except Exception as e:
            logging.error(f"Error during update price: {e}", exc_info=True)

    @staticmethod
    def controller_update_active(id, mount, is_income):
        db = Database()
        try:
            active = ActiveController.controller_fetch_active(id)
            if is_income:
                if active[4]:
                    BalanceController.controller_change_balance(
                        float(mount), True)
                    LiquidController.change(float(mount), True)
                else:
                    BalanceController.controller_change_balance(
                        float(mount), True)
                db.update_active(id, float(active[3]) + float(mount))
            else:
                if active[4]:
                    BalanceController.controller_change_balance(
                        float(mount), False)
                    LiquidController.change(float(mount), False)
                else:
                    BalanceController.controller_change_balance(
                        float(mount), False)
                db.update_active(id, float(active[3]) - float(mount))
        except Exception as e:
            logging.error(f"Error during update active: {e}", exc_info=True)

    @staticmethod
    def controller_intertransfer(source_id, target_id, mount):
        db = Database()
        try:
            source = ActiveController.controller_fetch_active(source_id)
            target = ActiveController.controller_fetch_active(target_id)
            created_at = datetime.now().astimezone().strftime("%d/%m/%Y %H:%M")
            if source[3] < float(mount):
                raise ValueError(
                    "No tienes saldo suficiente para realizar la transferencia")
            ActiveController.controller_update_active(source_id, mount, False)
            ActiveController.controller_update_active(target_id, mount, True)
            db.set_intertransaction(
                source[2], target[2], float(mount), created_at)
        except Exception as e:
            logging.error(f"Error during intertransfer: {e}", exc_info=True)
            raise e

    @staticmethod
    def controller_fetch_intertransactions():
        db = Database()
        try:
            intertransactions = db.fetch_intertransactions()
            return intertransactions
        except Exception as e:
            logging.error(f"Error during fetch intertransactions: {e}")
            return []

    @staticmethod
    def controller_delete_active(id):
        db = Database()
        try:
            active = ActiveController.controller_fetch_active(id)
            if active[4]:  # si el activo es liquido bajar de ambas
                BalanceController.controller_change_balance(active[3], False)
                LiquidController.change(active[3], False)
            else:
                BalanceController.controller_change_balance(active[3], False)
            db.delete_active(id)
        except Exception as e:
            logging.error(f"Error during delete active: {e}", exc_info=True)
