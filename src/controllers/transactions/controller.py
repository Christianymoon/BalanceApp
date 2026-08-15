from datetime import datetime
from enum import Enum
import logging

from controllers.actives.controller import ActiveController
from controllers.balance.controller import BalanceController
from controllers.passives.controller import PassiveController
from db.database import Database
from dto.transactions import (
    TransactionDTO,
    TransactionFilterDTO,
    TransactionOutputDTO,
    TransactionUpdateDTO,
)


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
    def fetch_transactions(filter: TransactionFilterDTO) -> list[TransactionOutputDTO]:
        try:
            db = Database()
            transactions = db.fetch_transactions(filter)
            return transactions
        except Exception as e:
            logging.error(f"Error fetching transactions: {e}", exc_info=True)
            return []

    @staticmethod
    def controller_fetch_sum(is_income=True) -> str:
        filter = TransactionFilterDTO()
        all_transactions = TransactionController.fetch_transactions(filter)
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
