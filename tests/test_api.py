from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app
from repositories.moderation import ModerationRulesRepository

client = TestClient(app)


@pytest.fixture
def ad() -> dict[str, int | bool | str]:
    return {
        "seller_id": 1,
        "is_verified_seller": False,
        "item_id": 42,
        "name": "Велосипед",
        "description": "В хорошем состоянии",
        "category": 3,
        "images_qty": 0,
    }


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


@pytest.mark.parametrize(
    ("is_verified_seller", "images_qty", "has_violation"),
    [(True, 0, False), (True, 1, False), (False, 1, False), (False, 0, True)],
)
def test_predict(ad, is_verified_seller, images_qty, has_violation):
    ad.update(is_verified_seller=is_verified_seller, images_qty=images_qty)

    response = client.post("/predict", json=ad)

    assert response.status_code == 200
    assert response.json() is has_violation


@pytest.mark.parametrize(
    ("field", "invalid_value", "error_type"),
    [
        ("seller_id", "1", "int_type"),
        ("is_verified_seller", 1, "bool_type"),
        ("item_id", True, "int_type"),
        ("name", 123, "string_type"),
        ("description", None, "string_type"),
        ("category", 1.5, "int_type"),
        ("images_qty", "1", "int_type"),
        ("images_qty", -1, "greater_than_equal"),
        ("unknown", 1, "extra_forbidden"),
    ],
)
def test_predict_rejects_invalid_field(ad, field, invalid_value, error_type):
    ad[field] = invalid_value

    response = client.post("/predict", json=ad)

    assert response.status_code == 400
    (error,) = response.json()["detail"]
    assert error["loc"] == ["body", field]
    assert error["type"] == error_type


@pytest.mark.parametrize(
    "field",
    [
        "seller_id",
        "is_verified_seller",
        "item_id",
        "name",
        "description",
        "category",
        "images_qty",
    ],
)
def test_predict_requires_field(ad, field):
    del ad[field]

    response = client.post("/predict", json=ad)

    assert response.status_code == 400
    (error,) = response.json()["detail"]
    assert error["loc"] == ["body", field]
    assert error["type"] == "missing"


def test_predict_rejects_malformed_json():
    response = client.post(
        "/predict", content="{", headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400
    (error,) = response.json()["detail"]
    assert error["type"] == "json_invalid"


def test_predict_returns_500_when_rule_lookup_fails(ad):
    with patch.object(
        ModerationRulesRepository,
        "minimum_images_for_unverified_seller",
        side_effect=RuntimeError("Ошибка чтения правил"),
    ):
        response = client.post("/predict", json=ad)

    assert response.status_code == 500
    assert response.json() == {"detail": "Не удалось проверить объявление"}
