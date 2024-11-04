from http import HTTPStatus

from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy.orm import Session

from currency_app.api.deps import get_db
from currency_app.api.utils import (
    add_order_to_table,
    get_order_with_converted_amount,
    put_order,
)
from currency_app.models.order import Order as OrderModel
from currency_app.schemas.order import (
    OrderCreateSchema,
    OrderGetSchema,
    OrderGetWithConvertedAmountSchema,
    OrderPutSchema,
)
from currency_app.settings import settings

app = FastAPI(
    title="Currency Exchange API",
    description="An API to convert currency",
    version=settings.version,
    docs_url="/",
)

orders = APIRouter(prefix="/orders", tags=["Orders"])


@orders.post("/", response_model=OrderGetSchema, status_code=HTTPStatus.CREATED)
async def create_order(order: OrderCreateSchema, db: Session = Depends(get_db)):
    return add_order_to_table(db, order)


@orders.put("/{order_id}", response_model=OrderGetSchema, status_code=HTTPStatus.OK)
async def update_order(
    order_id: str, order: OrderPutSchema, db: Session = Depends(get_db)
):
    return put_order(db, order_id, order)


@orders.get(
    "/{order_id}",
    response_model=OrderGetWithConvertedAmountSchema,
    status_code=HTTPStatus.OK,
)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    return get_order_with_converted_amount(db, order_id)


app.include_router(orders)
