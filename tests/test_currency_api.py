import json
from http import HTTPStatus
from typing import Any, Optional
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from currency_app.models.order import Order, OrderStatus


@pytest.fixture
def mock_nbp_client():
    with open("tests/rates.json") as f:
        rates = json.load(f)
    with patch("currency_app.clients.nbp_client.NBPClient._get_rates") as mock:
        mock.return_value = rates
        yield mock


def test_create_currency_should_return_proper_response(db_api, test_client: TestClient):
    response = test_client.post(
        "/orders",
        json={"customer_name": "Juan Pablo", "total_amount": 100.0, "currency": "USD"},
    )
    assert response.status_code == 201
    response_body = response.json()
    assert response_body["customer_name"] == "Juan Pablo"
    assert response_body["total_amount"] == 100.0
    assert response_body["currency"] == "USD"
    assert response_body["status"] == "Pending"
    assert response_body.get("id") is not None


def test_create_currency_should_create_record_in_db(db_api, test_client: TestClient):
    assert db_api.query(Order).count() == 0

    response = test_client.post(
        "/orders",
        json={"customer_name": "Juan Pablo", "total_amount": 100.0, "currency": "USD"},
    )

    assert db_api.query(Order).count() == 1


@pytest.mark.parametrize(
    "data",
    [
        {"customer_name": 1, "total_amount": 100.0, "currency": "USD"},
        {"customer_name": "J.T.", "total_amount": -20, "currency": "USD"},
        {"customer_name": "", "total_amount": 20, "currency": "USD"},
        {
            "customer_name": "Juan Pablo",
            "total_amount": "100 millions",
            "currency": "USD",
        },
        {"customer_name": "Test client", "total_amount": 100.0, "currency": "XDD"},
    ],
)
def test_create_currency_with_invalid_data_should_return_unprocessable_entity_response(
    db_api, test_client: TestClient, data: dict[str, Any]
):
    resp = test_client.post("/orders", json=data)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_put_non_existing_order_should_return_not_found_response(
    db_api, test_client: TestClient
):
    response = test_client.put(
        "/orders/5159262c-e4f3-4f61-ad40-d97e8a31ad70",
        json={
            "customer_name": "Juan Pablo",
            "total_amount": 100.0,
            "currency": "USD",
            "status": "Shipped",
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, response.text


def when_order_is_created(db_api, status: Optional[OrderStatus] = None) -> str:
    order = Order(
        customer_name="Juan Pablo",
        total_amount=100.0,
        currency="USD",
        status=status or OrderStatus.PENDING,
    )
    db_api.add(order)
    db_api.commit()
    return order.id


def test_put_existing_order_should_return_proper_response(
    db_api, test_client: TestClient
):
    order_id = when_order_is_created(db_api)

    response = test_client.put(
        f"/orders/{order_id}",
        json={
            "customer_name": "Adam SmallMouse",
            "total_amount": 99.99,
            "currency": "GBP",
            "status": "Delivered",
        },
    )
    assert response.status_code == HTTPStatus.OK, response.text
    response_body = response.json()
    assert response_body["customer_name"] == "Adam SmallMouse"
    assert response_body["total_amount"] == 99.99
    assert response_body["currency"] == "GBP"
    assert response_body["status"] == "Delivered"
    assert response_body["id"] == str(order_id)


def test_get_non_existing_order_should_return_not_found_response(
    db_api, test_client: TestClient
):
    response = test_client.get("/orders/5159262c-e4f3-4f61-ad40-d97e8a31ad70")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.text


def test_get_wrong_order_id_should_return_bad_request_response(
    db_api, test_client: TestClient
):
    response = test_client.get("/orders/123")
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.text


def test_get_existing_order_should_return_proper_response(
    db_api, test_client: TestClient, mock_nbp_client
):
    order_id = when_order_is_created(db_api)

    response = test_client.get(f"/orders/{order_id}")
    assert response.status_code == HTTPStatus.OK, response.text
    response_body = response.json()
    assert response_body["customer_name"] == "Juan Pablo"
    assert response_body["total_amount"] == 100.0
    assert response_body["currency"] == "USD"
    assert response_body["status"] == "Pending"
    assert response_body["id"] == str(order_id)
    assert response_body["converted_amount"] == 398.69


def test_get_list_of_orders_should_return_list_of_orders(
    db_api, test_client: TestClient
):
    [when_order_is_created(db_api) for _ in range(3)]

    response = test_client.get("/orders")
    assert response.status_code == HTTPStatus.OK, response.text
    response_body = response.json()
    assert len(response_body) == 3


def test_get_list_of_orders_with_shipped_status_should_return_list_of_orders_with_shipped_status(
    db_api, test_client: TestClient
):
    [when_order_is_created(db_api) for _ in range(10)]
    [when_order_is_created(db_api, status=OrderStatus.SHIPPED) for _ in range(5)]

    response = test_client.get("/orders?status=Shipped")
    assert response.status_code == HTTPStatus.OK, response.text
    response_body = response.json()
    assert len(response_body) == 5
    assert all([order["status"] == "Shipped" for order in response_body])
