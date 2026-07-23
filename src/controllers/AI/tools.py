from controllers.controller import (
    CategoriesController,
    TransactionController,
    ActiveController,
)
from dto.transactions import TransactionDTO, TransactionUpdateDTO
from enum import Enum


class TransactionType(Enum):
    INCOME = "income"
    SPENT = "spent"
    CREDIT = "credit"


gemini_tools = {
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
    },
}
