import decimal
from enum import Enum

from pydantic import BaseModel, Field


class Operations(str, Enum):
    """Supported operations"""

    deposit = 'DEPOSIT'
    withdraw = 'WITHDRAW'


class OperationRequest(BaseModel):
    """Model for operation request"""

    operationType: Operations  # noqa: N815
    amount: decimal.Decimal = Field(gt=0)
