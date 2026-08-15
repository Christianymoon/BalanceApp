import logging

from db.database import Database


class LiquidController:
    @staticmethod
    def set(amount):
        db = Database()
        try:
            db.set_liquid(float(amount))
        except Exception as e:
            logging.error(
                f"Error during set liquid to database {e}", exc_info=True)

    @staticmethod
    def get(formated=False):
        db = Database()
        try:
            liquid_obj = db.fetch_liquid()[1]
            if liquid_obj is None:
                raise ValueError("Liquid object is NoneType")
        except Exception as e:
            logging.error(
                f"Error during get liquid object {e} trying to setting up", exc_info=True)
            LiquidController.set(0)
            liquid_obj = db.fetch_liquid()[1]
        finally:
            if formated:
                return f"${liquid_obj:,.2f}"
            return liquid_obj

    @staticmethod
    def udpate(new_amount):
        """Update the last element on the database"""
        db = Database()
        try:
            db.udpate_liquid(new_amount)
        except Exception as e:
            logging.error(f"Error during update liquid {e}", exc_info=True)

    def change(new_amount, is_increase):
        try:
            if not is_increase:
                new_amount = -float(new_amount)
            else:
                new_amount = float(new_amount)

            LiquidController.udpate(new_amount)
        except Exception as e:
            logging.error(f"Error during change value {e}")
