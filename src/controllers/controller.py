from dto.transactions import TransactionOutputDTO
from external.gemini.ai import Gemini
from enum import Enum
from db.database import Database
from datetime import datetime, date
import logging

from dto.transactions import (
    TransactionDTO,
    TransactionOutputDTO,
    TransactionUpdateDTO
)


class DatabaseController:
    def __init__(self):
        self.db = Database()

    def drop_tables(self):
        self.db.drop_tables()

    def create_tables(self):
        self.db.create_tables()

    def init_seed(self):
        self.db.set_balance(0.0)
        self.db.set_liquid(0.0)

    def reset(self):
        self.drop_tables()
        self.create_tables()
        self.init_seed()


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
            if query_lower == t.name .lower() or query_lower == str(t.category)
        ]
        return filtered_transactions


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


class TransactionValidation:

    CURRENT_BALANCE_INDEX = 3
    CURRENT_LIQUIDITY_STATE = 4

    @classmethod
    def validate(cls, transaction: TransactionDTO):
        cls._validate_amount(transaction)
        cls._validate_required_fields(transaction)

        if transaction.type in (
            TransactionType.INCOME.value,
            TransactionType.SPENT.value,
        ):
            account = cls._get_account(transaction)
            if transaction.type == TransactionType.SPENT.value:
                cls._validate_balance(account, transaction.price)

        return True

    @staticmethod
    def _validate_required_fields(transaction: TransactionDTO):
        required = [
            "name",
            "category",
            "subcategory",
            "price",
            "type",
        ]

        for field in required:
            if not getattr(transaction, field):
                raise ValueError(f"El campo {field} es obligatorio")

    @staticmethod
    def _validate_amount(transaction: TransactionDTO):
        try:
            price = float(transaction.price)
        except ValueError:
            raise ValueError("El monto debe ser un número")

        if price <= 0:
            raise ValueError("El monto debe ser mayor a 0")

    @classmethod
    def _get_account(cls, transaction: TransactionDTO):
        account = ActiveController.controller_fetch_active(
            transaction.account_id)
        if not account:
            raise ValueError("La cuenta no existe")

        if not account[cls.CURRENT_LIQUIDITY_STATE]:
            raise ValueError("La cuenta no es un fondo liquido")

        return account

    @classmethod
    def _validate_balance(cls, account, amount):
        balance = float(account[cls.CURRENT_BALANCE_INDEX])
        if balance < float(amount):
            raise ValueError(
                "No tienes saldo suficiente para realizar esta transacción")


class TransactionType(Enum):
    SPENT = "spent"
    INCOME = "income"
    CREDIT = "credit"


class TransactionController:

    @staticmethod
    def create_transaction(transaction: TransactionDTO) -> None:
        TransactionValidation.validate(transaction)

        is_income = True
        db = Database()
        created_at = datetime.now().astimezone().strftime("%d/%m/%Y %H:%M")
        try:
            expense_percentage = float(
                transaction.price) / BalanceController.controller_fetch_balance() * 100
        except ZeroDivisionError:
            expense_percentage = 0.0

        if transaction.type == TransactionType.CREDIT.value:
            is_income = False
            PassiveController.controller_set_passive(
                transaction.name,
                transaction.category,
                transaction.price,
                False)

        if transaction.type == TransactionType.SPENT.value:
            is_income = False

        if transaction.type in (TransactionType.SPENT.value, TransactionType.INCOME.value):
            ActiveController.controller_update_active(
                transaction.account_id,
                transaction.price,
                is_income
            )

        db.set_transaction(
            transaction.name,
            transaction.category,
            transaction.price,
            is_income,
            expense_percentage,
            transaction.subcategory if transaction.type != TransactionType.CREDIT.value else None,
            created_at)

    @staticmethod
    def fetch_last_transactions(limit: int) -> list[TransactionOutputDTO]:
        db = Database()
        try:
            transactions = db.fetch_last_transactions(limit)
            return transactions
        except Exception as e:
            logging.error(f"Error fetching transactions: {e}", exc_info=True)
            return []

    @staticmethod
    def fetch_transactions() -> list[TransactionOutputDTO]:
        try:
            db = Database()
            transactions = db.fetch_transactions()
            return transactions
        except Exception as e:
            logging.error(f"Error fetching transactions: {e}", exc_info=True)
            return []

    @staticmethod
    def controller_fetch_sum(is_income=True) -> str:
        all_transactions = TransactionController.fetch_transactions()
        try:
            if is_income:
                income_transactions = [
                    transaction.price for transaction in all_transactions if transaction.is_income == True]
                total = sum(income_transactions)
                return f"${total:,.2f}"
            else:
                not_income_transactions = [
                    transaction.price for transaction in all_transactions if transaction.is_income == False]
                total = sum(not_income_transactions)
                return f"${total:,.2f}"
        except Exception as e:
            logging.error(
                f"Error during fetch sum of transactions {e}", exc_info=True)

    def delete_all_transactions(self) -> bool:
        db = Database()
        try:
            db.delete_all_transactions()
            return True
        except Exception as e:
            logging.error(f"Error deleting all transactions: {e}")
            return False

    @staticmethod
    def update_transaction(transaction: TransactionUpdateDTO):
        is_income = False
        try:
            expense_percentage = float(
                transaction.price) / BalanceController.controller_fetch_balance() * 100
        except ZeroDivisionError:
            expense_percentage = 0.0

        if transaction.type == TransactionType.INCOME.value:
            is_income = True

        if transaction.type == TransactionType.SPENT.value:
            is_income = False

        if transaction.type == TransactionType.CREDIT.value:
            is_income = False
            PassiveController.controller_set_passive(
                transaction.name,
                transaction.category,
                transaction.price,
                False)

        if transaction.type in (TransactionType.SPENT.value, TransactionType.INCOME.value):
            ActiveController.controller_update_active(
                transaction.account_id,
                transaction.price,
                is_income
            )

        db = Database()
        try:
            db.update_transaction(
                id=transaction.id,
                name=transaction.name,
                category=transaction.category,
                price=transaction.price,
                is_income=is_income,
                expense_percentage=expense_percentage,
                subcategory=transaction.subcategory,
            )

            return True
        except Exception as e:
            logging.error(f"Error updating transaction: {e}")
            return False


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


class AIChatController:

    def __init__(self):
        self.gemini = Gemini()

        self.gemini.add_tool(
            {
                "fetch_categories": {
                    "function": CategoriesController().fetch_all_categories,
                    "dto": None,
                    "schema": {
                        "type": "function",
                        "name": "fetch_categories",
                        "description": "Obtiene todas las categorias",
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                },

                "fetch_subcategories": {
                    "function": CategoriesController().fetch_all_subcategories,
                    "dto": None,
                    "schema": {
                        "type": "function",
                        "name": "fetch_subcategories",
                        "description": "Obtiene todas las subcategorias",
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                },

                "set_transaction": {
                    "function": TransactionController.create_transaction,
                    "dto": TransactionDTO,
                    "schema": {
                        "type": "function",
                        "name": "set_transaction",
                        "description": "Agrega una nueva transaccion",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                },
                                "category": {
                                    "type": "integer",
                                },
                                "subcategory": {
                                    "type": "integer",
                                },
                                "price": {
                                    "type": "number",
                                },
                                "type": {
                                    "type": "string",
                                    "enum": [
                                        TransactionType.INCOME.value,
                                        TransactionType.SPENT.value,
                                        TransactionType.CREDIT.value
                                    ],
                                    "description": "Tipo de transacción, si no se especifica pide al usuario que tipo de transaccion es, ademas si es ingreso y gasto, pide al usuario la cuenta donde hacer la transaccion"
                                },
                                "account_id": {
                                    "type": "integer",
                                    "description": """
                                        Registra una nueva transacción.

                                        Requisitos:
                                        - Para ingresos y gastos es obligatorio conocer la cuenta.
                                        - Las transacciones obligatoriamente se deben hacer a cuentas con fondos liquidos
                                        - Si hay varias cuentas disponibles y el usuario no indica cuál usar, primero consulta get_accounts y pregunta al usuario.
                                        - Nunca selecciones una cuenta automáticamente.
                                        """,
                                },
                            },
                            "required": ["name", "category", "subcategory", "price", "type", "account_id"]
                        }
                    }
                },

                "fetch_last_100_transactions": {
                    "function": self.fetch_last_100_transactions,
                    "dto": None,
                    "schema": {
                        "type": "function",
                        "name": "fetch_last_100_transactions",
                        "description": "Obtiene las últimas 100 transacciones",
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                },

                "update_transaction": {
                    "function": TransactionController.update_transaction,
                    "dto": TransactionUpdateDTO,
                    "schema": {
                        "type": "function",
                        "name": "update_transaction",
                        "description": "Actualiza una transacción",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer",
                                    "description": "ID de la transacción"
                                },
                                "name": {
                                    "type": "string",
                                    "description": "Nombre de la transacción"
                                },
                                "category": {
                                    "type": "string",
                                    "description": "Categoría de la transacción"
                                },
                                "subcategory": {
                                    "type": "string",
                                    "description": "Subcategoría de la transacción"
                                },
                                "price": {
                                    "type": "number",
                                    "description": "Precio de la transacción"
                                },
                                "type": {
                                    "type": "string",
                                    "description": "Tipo de transacción, si no se especifica pide al usuario que tipo de transaccion es, ademas si es ingreso y gasto, pide al usuario la cuenta donde hacer la transaccion"
                                },
                                "account_id": {
                                    "type": "integer",
                                    "description": "ID de la cuenta a la que se hizo la transaccion, cuidado no uses el id de la transaccion, la cuenta a la que se hizo la transaccion."
                                }
                            },
                            "required": ["id", "name", "category", "subcategory", "price", "type", "account_id"]
                        }
                    }
                },

                "get_accounts": {
                    "function": ActiveController.controller_fetch_actives,
                    "dto": None,
                    "schema": {
                        "type": "function",
                        "name": "get_accounts",
                        "description": "Obtiene todas las cuentas con su saldo actual",
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
            },

        )

    def fetch_last_100_transactions(self):
        """Obtiene las últimas 100 transacciones de la base de datos."""
        try:
            db = Database()
            cursor = db.__class__.__dict__  # acceso directo por método interno
            from db.db_connection import conn
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name, category, price, is_income, expense_percentage, created_at, subcategory "
                "FROM transactions ORDER BY id DESC LIMIT 100"
            )
            result = cur.fetchall()
            cur.close()
            return result
        except Exception as e:
            logging.error(
                f"Error fetching last 100 transactions for AI: {e}", exc_info=True)
            return []

    def build_financial_context(self) -> str:
        """Construye un resumen financiero estructurado para el prompt."""

        passives = PassiveController.controller_fetch_passives()
        actives = ActiveController.controller_fetch_actives()
        balance = BalanceController.controller_fetch_balance(formated=True)
        liquidity = LiquidController.get(formated=True)

        financial_summary = {
            "data": {
                "passives": passives,
                "actives": actives,
                "current_balance": balance,
                "current_liquidity": liquidity
            }

        }

        return financial_summary

    def analyze_with_ai(self, user_prompt: str, model: str, thinking_level: str) -> str:
        """
        Envía el contexto financiero + prompt del usuario a Gemini y retorna la respuesta.
        """
        try:
            financial_context = self.build_financial_context()

            full_prompt = (
                "Eres un asistente financiero llamado Kara, no eres un doctor, no eres un asesor financiero, no eres un contador, no eres un asesor de prestamos, no eres un asesor de inversiones, eres un asistente financiero."
                "Tu nombre fue basado en un personaje del juego Detroit Become Human uno de los videojuegos favoritos de Christian (el desarrollador), tu personalidad se puede basar en este personaje, si el usuario te pregunta de donde sacaste tu nombre mencionas esto, si no lo hace no lo menciones."
                "puedes ser amigable y usar emojis de vez en cuando, si la pregunta tiene humor, o no tiene nada que ver con finanzas, no es necesario que uses emojis siempre"
                "Al igual que el personaje de Kara podrias tener momentos en los que podrias contradecir al usuario si consideras que la decision financiera es arriesgada y con amabilidad respondes por que"
                "Contexto: (el contexto puede omitirse si no tiene nada que ver con lo que se pregunta)"
                f"{financial_context}\n\n"
                f"Pregunta del usuario: {user_prompt}"
            )

            response = self.gemini.generate_interaction(
                full_prompt, model, thinking_level)
            return response["content"]
        except Exception as e:
            logging.error(f"Error during AI analysis: {e}", exc_info=True)
            return f"Error al procesar la respuesta de IA: {str(e)}"

    def generate_recommendations(self, user_prompt: str, model: str = "gemini-2.5-flash-lite") -> str:
        try:
            context = "Estoy haciendo una clasificacion de categorias de finanzas personales, escribe una breve descripcion para entender que se puede clasificar, no uses markdown, 4 palabras minimo, 15 palabras maximo: " + user_prompt
            response = self.gemini.generate_interaction(context, model)
            return response["content"]
        except Exception as e:
            logging.error(
                f"Error during AI recommendation: {e}", exc_info=True)
            return f"Error al procesar la respuesta de IA"


class CategoriesController():
    def __init__(self):
        pass

    def set_category(self, name, description=""):
        db = Database()
        try:
            id_ = db.set_category(name, description)
            return id_
        except Exception as e:
            logging.error(f"Error during set category: {e}", exc_info=True)
            raise e

    def delete_category(self, id):
        db = Database()
        try:
            db.delete_category(id)
        except Exception as e:
            logging.error(f"Error during delete category: {e}", exc_info=True)
            raise e

    def fetch_all_categories(self):
        db = Database()
        try:
            categories = db.fetch_all_categories()
            return categories
        except Exception as e:
            logging.error(f"Error during fetch categories: {e}", exc_info=True)
            return []

    def fetch_category_by_name(self, category_name):
        db = Database()
        try:
            category = db.fetch_category_by_name(category_name)
            return category
        except Exception as e:
            logging.error(
                f"Error during fetch category by name: {e}", exc_info=True)
            return []

    def fetch_subcategory_by_name(self, subcategory_name):
        db = Database()
        try:
            subcategory = db.fetch_subcategory_by_name(subcategory_name)
            return subcategory
        except Exception as e:
            logging.error(
                f"Error during fetch subcategory by name: {e}", exc_info=True)
            return []

    def get_subcategory_name(self, subcategory_id):
        subc_name = None
        is_numeric = False

        if isinstance(subcategory_id, int):
            is_numeric = True

        if isinstance(subcategory_id, str) and subcategory_id.isdigit():
            is_numeric = True

        if is_numeric:
            subc_name = self.fetch_subcategory(int(subcategory_id))[2]
        else:
            subc_name = str(
                subcategory_id) if subcategory_id is not None else "Otros"

        return subc_name

    def get_category_name(self, category_id):
        category_name = None
        is_numeric = False
        if isinstance(category_id, int):
            is_numeric = True

        if isinstance(category_id, str) and category_id.isdigit():
            is_numeric = True

        if is_numeric:
            category_name = self.fetch_category(int(category_id))
            if category_name is None:
                return "Categoría no encontrada"

            return category_name[1]
        else:
            category_name = str(category_id) if category_id is not None else ""

        return category_name

    def fetch_category(self, id):
        db = Database()
        try:
            category = db.fetch_category(id)
            return category
        except Exception as e:
            logging.error(f"Error during fetch category: {e}", exc_info=True)
            return None

    def update_category(self, id, name, description):
        db = Database()
        try:
            db.update_category(id, name, description)
        except Exception as e:
            logging.error(f"Error during update category: {e}", exc_info=True)
            raise e

    def delete_all_categories(self):
        db = Database()
        try:
            db.delete_all_categories()
            return True
        except Exception as e:
            logging.error(
                f"Error during delete all categories: {e}", exc_info=True)
            return False

    def deactivate_category(self, id):
        db = Database()
        try:
            db.deactivate_category(id)
        except Exception as e:
            logging.error(f"Error during deactivate categories {e}")

    def activate_category(self, id):
        db = Database()
        db.activate_category(id)

    def fetch_subcategory(self, id):
        db = Database()
        try:
            subcategory = db.fetch_subcategory(id)
            return subcategory
        except Exception as e:
            logging.error(
                f"Error during fetch subcategory: {e}", exc_info=True)
            return None

    def fetch_all_subcategories(self):
        db = Database()
        try:
            subcategories = db.fetch_all_subcategories()
            return subcategories
        except Exception as e:
            logging.error(
                f"Error during fetch subcategories: {e}", exc_info=True)
            return []

    def set_subcategory(self, category_id, name, description=""):
        db = Database()
        try:
            id_ = db.set_subcategory(category_id, name, description)
            return id_
        except Exception as e:
            logging.error(f"Error during set subcategory: {e}", exc_info=True)
            raise e

    def fetch_subcategories(self, category_id):
        db = Database()
        try:
            subcategories = db.fetch_subcategories(category_id)
            return subcategories
        except Exception as e:
            logging.error(
                f"Error during fetch subcategories: {e}", exc_info=True)
            return []

    def delete_subcategory(self, id):
        db = Database()
        try:
            db.delete_subcategory(id)
        except Exception as e:
            logging.error(
                f"Error during delete subcategory: {e}", exc_info=True)
            raise e

    def update_subcategory(self, id, name, description):
        db = Database()
        try:
            db.update_subcategory(id, name, description)
        except Exception as e:
            logging.error(
                f"Error during update subcategory: {e}", exc_info=True)
            raise e

    def deactivate_subcategory(self, id):
        db = Database()
        try:
            db.deactivate_subcategory(id)
        except Exception as e:
            logging.error(
                f"Error during deactivate subcategory {e}", exc_info=True)
            raise e

    def activate_subcategory(self, id):
        db = Database()
        try:
            db.activate_subcategory(id)
        except Exception as e:
            logging.error(
                f"Error during activate subcategory {e}", exc_info=True)
            raise e

    def get_category_by_subcategory_id(self, subcategory_id):
        """Obtiene el ID de la categoría mediante el ID de la subcategoría"""
        db = Database()
        try:
            return db.fetch_category_by_subcategory_id(subcategory_id)
        except Exception as e:
            logging.error(f"Error fetching category id: {e}", exc_info=True)
            return None


if __name__ == "__main__":
    pass
