from database import Database
import logging
import httpx
from datetime import datetime
from zoneinfo import ZoneInfo

class DatabaseController:
    def __init__(self):
        self.db = Database()

    def create_tables(self):
        self.db.create_tables()

    def drop_tables(self):
        self.db.drop_tables()
        
    def init_seed(self):
        self.db.set_balance(0.0)
        self.db.set_liquid(0.0)

class UserDataController:
    @staticmethod
    def controller_set_userdata(name, gender):
        if not name:
            name = ""
        db = Database()
        db.set_userdata(name, gender)
        

    @staticmethod    
    def controller_fetch_userdata():
        db = Database()
        user_data = db.fetch_userdata()  # return a tuple
        
        return user_data
    
class SearchController:
    def __init__(self):
        pass
    
    def controller_search_transactions(query):
        db = Database()
        transactions = db.fetch_transactions()
        
        query_lower = query.lower()
        filtered_transactions = [
            t for t in transactions
            if query_lower == t[1].lower() or query_lower == t[2].lower()
        ]
        return filtered_transactions

class PassiveController:
    @staticmethod
    def controller_set_passive(name, category, amount, is_liquidated=False):
        db = Database()
        try:
            created_at = datetime.now().astimezone().strftime("%d/%m/%Y %H:%M")
            db.set_passive(name, category, amount, is_liquidated, created_at)
            TransactionController.register_transaction(name, category, amount, False, created_at)
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
                raise ValueError("No tienes saldo suficiente para pagar este pasivo")
            if passive and not passive[4]:
                db.update_passive(id)
                db.update_active(active_id, active[3] - passive[3])
                LiquidController.change(passive[3], False)
        except Exception as e:
            logging.error(f"Error during paying passive: {e}", exc_info=True)
            raise e
        
    @staticmethod
    def controller_fetch_passives():
        db = Database()
        try:
            all_passives = db.fetch_passives()
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

        BalanceController.controller_set_balance(amount) # updates now only
    
    def fetch_balance_update():
        db = Database()
        return db.fetch_balance()[2]

class TransactionController:
    @staticmethod
    def controller_set_transaction(data): 
        if data["type"] == "credit":
            PassiveController.controller_set_passive(
                data["name"], 
                data["category"], 
                data["price"], 
                False)
            return

        if not TransactionController.validate_transaction(data) and data["type"] == "spent":
            raise Exception("No hay saldo suficiente para realizar la transaccion")

        db = Database()

        if data["type"] == "spent":
            is_income = False
        elif data["type"] == "income":
            is_income = True

        

        created_at = datetime.now().astimezone().strftime("%d/%m/%Y %H:%M")

        try:
            expense_percentage = float(data["price"]) / BalanceController.controller_fetch_balance() * 100
        except ZeroDivisionError:
            expense_percentage = 0.0
        db.set_transaction(
            data["name"], 
            data["category"], 
            data["price"], 
            is_income, 
            expense_percentage, 
            created_at)
    
        ActiveController.controller_update_active(
            data["account_id"], 
            data["price"], 
            is_income
        )

    def register_transaction(name, category, price, is_income, created_at):
        db = Database()
        try:
            expense_percentage = float(price) / BalanceController.controller_fetch_balance() * 100
        except ZeroDivisionError:
            expense_percentage = 0.0
        db.set_transaction(
            name, 
            category, 
            price, 
            is_income, 
            expense_percentage, 
            created_at)

    def validate_transaction(data):
        active = ActiveController.controller_fetch_active(data["account_id"])
        if active[3] < float(data["price"]):
            return False
        return True

    @staticmethod
    def controller_fetch_transactions():
        try:
            db = Database()
            transactions = db.fetch_transactions()
            return transactions
        except Exception as e:
            logging.error(f"Error fetching transactions: {e}", exc_info=True)
            return []
    
    @staticmethod
    def controller_fetch_sum(is_income=True):
        all_transactions = TransactionController.controller_fetch_transactions()
        try:
            if is_income:
                income_transactions = [transaction[3] for transaction in all_transactions if transaction[4] == True]
                total = sum(income_transactions)
                return f"${total:,.2f}"
            else:
                not_income_transactions = [transaction[3] for transaction in all_transactions if transaction[4] == False]
                total = sum(not_income_transactions)
                return f"${total:,.2f}"
        except Exception as e:
            logging.error(f"Error during fetch sum of transactions {e}", exc_info=True)

class LiquidController:
    @staticmethod
    def set(amount):
        db = Database()
        try:
            db.set_liquid(float(amount))
        except Exception as e:
            logging.error(f"Error during set liquid to database {e}", exc_info=True)

    @staticmethod
    def get(formated=False):
        db = Database()
        try:
            liquid_obj = db.fetch_liquid()[1]
            if liquid_obj is None:
                raise ValueError("Liquid object is NoneType")
        except Exception as e:
            logging.error(f"Error during get liquid object {e} trying to setting up", exc_info=True)
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
            logging.error(f"Error during fetching all actives: {e}", exc_info=True)
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
    def controller_update_active(id, mount, is_income):
        db = Database()
        try:
            active = ActiveController.controller_fetch_active(id)
            if is_income:
                if active[4]:
                    BalanceController.controller_change_balance(float(mount), True)
                    LiquidController.change(float(mount), True)
                else:
                    BalanceController.controller_change_balance(float(mount), True)
                db.update_active(id, float(active[3]) + float(mount))
            else:
                if active[4]:
                    BalanceController.controller_change_balance(float(mount), False)
                    LiquidController.change(float(mount), False)
                else:
                    BalanceController.controller_change_balance(float(mount), False)
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
                raise ValueError("No tienes saldo suficiente para realizar la transferencia")
            ActiveController.controller_update_active(source_id, mount, False)
            ActiveController.controller_update_active(target_id, mount, True)
            db.set_intertransaction(source[2], target[2], float(mount), created_at)
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
            if active[4]: # si el activo es liquido bajar de ambas
                BalanceController.controller_change_balance(active[3], False)
                LiquidController.change(active[3], False)
            else:
                BalanceController.controller_change_balance(active[3], False)
            db.delete_active(id)
        except Exception as e:
            logging.error(f"Error during delete active: {e}", exc_info=True)

class LoanController:
    def __init__(self):
        pass 

    @staticmethod
    def calculate_interest(amount, interest):
        try:
            total_interest = float(amount) * (float(interest) / 100)
            return total_interest
        except Exception as e:
            logging.error(f"Error during calculate interest {e}", exc_info=True)
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
            ActiveController.controller_update_active(pay_account_id, float(loan[3]), True)
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
            PassiveController.controller_set_passive(name, "Prestamo", float(amount), False)
            active_id = ActiveController.controller_set_active(name, "Prestamo", float(amount), False)
            total_payment = LoanController.calculate_interest(amount, interest) + float(amount)
            created_at = datetime.now().astimezone().strftime("%d/%m/%Y %H:%M")
            db.set_borrowing(active_id, name, amount, interest, total_payment, created_at)
            return
        try:
            account = ActiveController.controller_fetch_active(_id)
            if account[3] < float(amount):
                raise Exception("No hay suficiente saldo en la cuenta")

            if account and account[4]:
                ActiveController.controller_update_active(_id, float(amount), False) # Baja liquidez
                active_id = ActiveController.controller_set_active(name, "Prestamo", float(amount), False) # Crea activo no liquido
                total_payment = LoanController.calculate_interest(amount, interest) + float(amount)
                created_at = datetime.now().astimezone().strftime("%d/%m/%Y %H:%M")
                db.set_borrowing(active_id, name, amount, interest, total_payment, created_at)
        except Exception as e:
            logging.error(f"Error during set loan {e}", exc_info=True)
            raise e


if __name__ == "__main__":
    pass
