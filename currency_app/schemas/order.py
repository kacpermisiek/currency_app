import uuid
from enum import Enum

from pydantic import BaseModel, field_validator
from pydantic.config import ConfigDict
from pydantic.fields import Field

from currency_app.models.order import OrderStatus


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class OrderCreateSchema(BaseModel):
    customer_name: str = Field(..., min_length=1)
    total_amount: float = Field(..., gt=0)
    currency: Currency


class OrderPutSchema(OrderCreateSchema):
    status: OrderStatus


class OrderGetSchema(BaseModel):
    id: str
    customer_name: str
    total_amount: float
    currency: Currency
    status: OrderStatus

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    def id_to_str(cls, v):
        return str(v)


class OrderGetWithConvertedAmountSchema(OrderGetSchema):
    converted_amount: float
