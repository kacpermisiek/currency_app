from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session

from currency_app.clients.nbp_client import NBPClient
from currency_app.models.order import Order as OrderModel
from currency_app.schemas.order import (
    OrderCreateSchema,
    OrderGetSchema,
    OrderGetWithConvertedAmountSchema,
    OrderPutSchema,
)


def add_order_to_table(db: Session, order: OrderCreateSchema) -> OrderGetSchema:
    try:
        new_order = OrderModel(**order.model_dump())
        db.add(new_order)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Object already exists or other error occurred"
        )
    return OrderGetSchema.model_validate(new_order)


def get_orders_list(db: Session, status: Optional[str]) -> list[OrderGetSchema]:
    query = db.query(OrderModel)
    if status is not None:
        query = query.filter(OrderModel.status == status)
    return [OrderGetSchema.model_validate(order) for order in query.all()]


def get_order_by_id(db: Session, order_id: str) -> OrderModel:
    try:
        order = db.query(OrderModel).get(order_id)
    except DataError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Invalid order id"
        )
    if order is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Order not found")
    return order


def get_converted_amount(total_amount, currency):
    nbp_client = NBPClient()
    rate = nbp_client.get_currency_rate(currency)
    return round(total_amount * rate, 2)


def get_order_with_converted_amount(db: Session, order_id: str) -> OrderGetSchema:
    order = get_order_by_id(db, order_id)
    return OrderGetWithConvertedAmountSchema(
        id=order.id,
        customer_name=order.customer_name,
        total_amount=order.total_amount,
        currency=order.currency,
        status=order.status,
        converted_amount=get_converted_amount(order.total_amount, order.currency),
    )


def put_order(db: Session, order_id: str, order: OrderPutSchema) -> OrderGetSchema:
    db_order = get_order_by_id(db, order_id)
    update_data = order.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(db_order, field, value)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Object already exists or other error occurred"
        )
    return OrderGetSchema.model_validate(db_order)
