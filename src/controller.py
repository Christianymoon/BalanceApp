from database import Database
import logging
import httpx

class DatabaseController:
    def __init__(self):
        self.db = Database()

    def create_tables(self):
        self.db.create_tables()

    def drop_tables(self):
        self.db.drop_tables()

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
    def controller_set_passive(name, category, amount, is_liquidated):
        db = Database()
        try:
            db.set_passive(name, category, amount, is_liquidated)
        except Exception as e:
            logging.error(f"Error during setting passive: {e}", exc_info=True)
        
        if is_liquidated:
            TransactionController.controller_set_transaction(name, category, amount, False)
        else:
            BalanceController.controller_change_balance(amount, False)
            
    def liquidate_passive(id):
        db = Database()
        try:
            passive = db.search_passive(id)
            if passive and not passive[4]:
                db.update_passive(id)
                LiquidController.change(passive[3], False) # False to increase liquidity
        except Exception as e:
            logging.error(f"Error during searching pasive on database: {e}")
        
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
    def controller_set_transaction(name, category, price, is_income, account_id): 
        """Transaction low both Balance and Liquidity"""
        db = Database()       
        try:
            expense_percentage = float(price) / BalanceController.controller_fetch_balance() * 100
        except ZeroDivisionError:
            expense_percentage = 0.0
        db.set_transaction(name, category, price, is_income, expense_percentage)
        ActiveController.controller_update_active(account_id, price, is_income)

    @staticmethod
    def delete_all(affect_amounts=True):
        db = Database()
        try: 
            all_transactions = TransactionController.controller_fetch_transactions()
            if affect_amounts:
                income_amounts = [transaction[3] for transaction in all_transactions if transaction[4] == True]
                not_income_amounts = [transaction[3] for transaction in all_transactions if transaction[4] == False]
                BalanceController.controller_change_balance(sum(income_amounts), False)
                BalanceController.controller_change_balance(sum(not_income_amounts), True)
                LiquidController.change(sum(income_amounts), False)
                LiquidController.change(sum(not_income_amounts), True)
            db.delete_all_transactions()
        except Exception as e:
            logging.error(f"Error during deleting transactions {e}")
        
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
    def controller_set_active(active_type, name, amount, is_liquid):
        db = Database()
        try:
            db.set_active(active_type, name, amount, is_liquid)
        except Exception as e:
            logging.error(f"Error during set active {e}")

        if is_liquid:
            BalanceController.controller_change_balance(amount, True)
            LiquidController.change(amount, True)
        else:
            BalanceController.controller_change_balance(amount, True)


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

class NewsController:
    def __init__(self):
        self.endpoint = "https://balance-news.onrender.com/news"
        
    def get_news(self):
        try:
            data = httpx.get(self.endpoint, timeout=10)
            parsed_data = data.json()
            return parsed_data
        
        except Exception as e:
            logging.error(f"Error during get news {e}")
            return []

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

    def set(name, amount, interest, _id, to, _from):
        db = Database()
        try:
            liquid_account = ActiveController.controller_fetch_active(_id)
            if liquid_account and liquid_account[4]:
                ActiveController.controller_update_active(_id, float(amount), False) # Baja liquidez
                ActiveController.controller_set_active("Prestamo", name, float(amount), False) # Crea activo no liquido
                total_payment = LoanController.calculate_interest(amount, interest) + float(amount)
                db.set_borrowing(name, amount, interest, total_payment)
        except Exception as e:
            logging.error(f"Error during set loan {e}", exc_info=True)


if __name__ == "__main__":
    pass
