import enum
import uuid

from sqlalchemy import Column, Enum, Float, String
from sqlalchemy.dialects.postgresql import UUID

from currency_app.db import Base


class OrderStatus(str, enum.Enum):
    PENDING = "Pending"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID, primary_key=True, default=str(uuid.uuid4()))
    customer_name = Column(String(255), nullable=False)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(16), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
