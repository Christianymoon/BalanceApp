from datetime import date
from enum import Enum

from controllers.actives.controller import ActiveController
from controllers.categories.controller import CategoriesController
from controllers.transactions.controller import TransactionController
from controllers.transactions.statistics import fetch_summary
from dto.transactions import (
    TransactionDTO,
    TransactionFilterDTO,
    TransactionUpdateDTO,
)


class TransactionType(Enum):
    INCOME = "income"
    SPENT = "spent"
    CREDIT = "credit"


gemini_tools = {

    "fetch_transactions": {
        "function": TransactionController.fetch_transactions,
        "dto": TransactionFilterDTO,
        "schema": {
            "type": "function",
            "name": "fetch_transactions",
            "description": "Obtiene todas las transacciones",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Limite de transacciones a obtener"
                    },
                    "date_from": {
                        "type": "string",
                        "description": """Fecha de inicio en formato yyyy-mm-dd, si no se especifica avisa al usuario que puedes calcularlo a partir de la fecha del inicio de semana de la actual fecha"""
                    },
                    "date_to": {
                        "type": "string",
                        "description": """Fecha de fin en formato yyyy-mm-dd, si no se especifica avisa al usuario que puedes calcularlo a partir de la fecha de hoy"""
                    },
                    "category_id": {
                        "type": "integer",
                        "description": "ID de la categoría"
                    },
                    "subcategory_id": {
                        "type": "integer",
                        "description": "ID de la subcategoría"
                    },
                    "is_income": {
                        "type": "boolean",
                        "description": "Indica si la transacción es un ingreso o egreso"
                    }
                }
            }
        }
    },

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

    "fetch_summary": {
        "function": fetch_summary,
        "dto": TransactionFilterDTO,
        "schema": {
            "type": "function",
            "name": "fetch_summary",
            "description": "Obtiene el resumen de transacciones",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Limite de transacciones a obtener"
                    },
                    "date_from": {
                        "type": "string",
                        "description": "Fecha de inicio en formato yyyy-mm-dd"
                    },
                    "date_to": {
                        "type": "string",
                        "description": "Fecha de fin en formato yyyy-mm-dd"
                    },
                    "category_id": {
                        "type": "integer",
                        "description": "ID de la categoría"
                    },
                    "subcategory_id": {
                        "type": "integer",
                        "description": "ID de la subcategoría"
                    },
                    "is_income": {
                        "type": "boolean",
                        "description": "Indica si es ingreso o egreso"
                    },
                },
                "required": []
            }
        }
    },

    "fetch_today": {
        "function": date.today,
        "dto": None,
        "schema": {
            "type": "function",
            "name": "fetch_today",
            "description": "Obtiene el dia de hoy",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
}
