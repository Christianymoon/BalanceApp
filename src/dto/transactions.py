from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class TransactionDTO:
    name: str
    category: int
    subcategory: int
    price: float
    type: str
    account_id: Optional[int] = None


@dataclass
class TransactionOutputDTO:
    id: int
    name: str
    category: int
    subcategory: int
    price: float
    is_income: bool
    expense_percentage: str
    created_at: Optional[datetime] = None


@dataclass
class TransactionUpdateDTO:
    id: int
    name: str
    category: int
    subcategory: int
    price: float
    type: str
    account_id: Optional[int] = None


@dataclass
class TransactionFilterDTO:
    limit: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    is_income: Optional[bool] = None
