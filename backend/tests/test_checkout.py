def test_create_checkout_saves_sale_and_items(
    client, test_business, auth_headers
):
    service_response = client.post(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
        json={
            "name": "Haircut",
            "price": "25.00",
            "duration_minutes": 30,
        },
    )
    assert service_response.status_code == 201, service_response.text
    service_id = service_response.json()["id"]

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/checkout",
        headers=auth_headers,
        json={
            "items": [
                {
                    "service_id": service_id,
                    "quantity": 2,
                }
            ],
            "notes": "Test checkout",
        },
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["subtotal"] == "50.00"
    assert data["discount_amount"] == "0.00"
    assert data["total_amount"] == "50.00"
    assert data["status"] == "pending"
    assert data["notes"] == "Test checkout"
    assert len(data["items"]) == 1
    assert data["items"][0]["service_name"] == "Haircut"
    assert data["items"][0]["quantity"] == 2
    assert data["items"][0]["line_total"] == "50.00"

    sale_response = client.get(
        f"/api/v1/businesses/{test_business.id}/checkout/{data['id']}",
        headers=auth_headers,
    )
    assert sale_response.status_code == 200, sale_response.text
    assert sale_response.json()["id"] == data["id"]


def test_checkout_sale_is_isolated_by_business(
    client, db_session, test_business, auth_headers
):
    from app.models.business import Business

    service_response = client.post(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
        json={
            "name": "Haircut",
            "price": "25.00",
            "duration_minutes": 30,
        },
    )
    assert service_response.status_code == 201, service_response.text

    checkout_response = client.post(
        f"/api/v1/businesses/{test_business.id}/checkout",
        headers=auth_headers,
        json={
            "items": [
                {"service_id": service_response.json()["id"], "quantity": 1}
            ]
        },
    )
    assert checkout_response.status_code == 201, checkout_response.text
    sale_id = checkout_response.json()["id"]

    other_business = Business(
        name="Other Salon",
        email="other-checkout@example.com",
    )
    db_session.add(other_business)
    db_session.commit()
    db_session.refresh(other_business)

    response = client.get(
        f"/api/v1/businesses/{other_business.id}/checkout/{sale_id}",
        headers=auth_headers,
    )

    assert response.status_code == 404, response.text


def test_checkout_rejects_service_from_another_business(
    client, db_session, test_business, auth_headers
):
    from app.models.business import Business
    from app.models.service import Service

    other_business = Business(
        name="Other Salon",
        email="other-service-checkout@example.com",
    )
    db_session.add(other_business)
    db_session.flush()

    other_service = Service(
        business_id=other_business.id,
        name="Other Salon Haircut",
        price=25,
        duration_minutes=30,
        is_active=True,
    )
    db_session.add(other_service)
    db_session.commit()
    db_session.refresh(other_service)

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/checkout",
        headers=auth_headers,
        json={
            "items": [
                {"service_id": str(other_service.id), "quantity": 1}
            ]
        },
    )

    assert response.status_code == 400, response.text
    assert "inactive or not in this business" in response.json()["detail"]


def test_checkout_applies_percentage_coupon(
    client, test_business, auth_headers
):
    service_response = client.post(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
        json={
            "name": "Haircut",
            "price": "100.00",
            "duration_minutes": 30,
        },
    )
    assert service_response.status_code == 201, service_response.text

    coupon_response = client.post(
        f"/api/v1/businesses/{test_business.id}/coupons",
        headers=auth_headers,
        json={
            "code": "WELCOME10",
            "discount_type": "percentage",
            "discount_value": "10.00",
            "minimum_spend": "0.00",
            "usage_limit": 10,
            "is_active": True,
        },
    )
    assert coupon_response.status_code == 201, coupon_response.text

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/checkout",
        headers=auth_headers,
        json={
            "coupon_code": "welcome10",
            "items": [
                {
                    "service_id": service_response.json()["id"],
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["subtotal"] == "100.00"
    assert data["discount_amount"] == "10.00"
    assert data["total_amount"] == "90.00"
    assert data["coupon_code"] == "WELCOME10"


def test_checkout_applies_fixed_amount_coupon(
    client, test_business, auth_headers
):
    service_response = client.post(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
        json={
            "name": "Haircut",
            "price": "100.00",
            "duration_minutes": 30,
        },
    )
    assert service_response.status_code == 201, service_response.text

    coupon_response = client.post(
        f"/api/v1/businesses/{test_business.id}/coupons",
        headers=auth_headers,
        json={
            "code": "SAVE20",
            "discount_type": "fixed",
            "discount_value": "20.00",
            "minimum_spend": "0.00",
            "usage_limit": 10,
            "is_active": True,
        },
    )
    assert coupon_response.status_code == 201, coupon_response.text

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/checkout",
        headers=auth_headers,
        json={
            "coupon_code": "SAVE20",
            "items": [
                {
                    "service_id": service_response.json()["id"],
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["subtotal"] == "100.00"
    assert data["discount_amount"] == "20.00"
    assert data["total_amount"] == "80.00"
    assert data["coupon_code"] == "SAVE20"


def test_checkout_rejects_coupon_when_usage_limit_reached(
    client, test_business, auth_headers
):
    service_response = client.post(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
        json={
            "name": "Haircut",
            "price": "100.00",
            "duration_minutes": 30,
        },
    )
    assert service_response.status_code == 201, service_response.text

    coupon_response = client.post(
        f"/api/v1/businesses/{test_business.id}/coupons",
        headers=auth_headers,
        json={
            "code": "LIMITED",
            "discount_type": "fixed",
            "discount_value": "10.00",
            "minimum_spend": "0.00",
            "usage_limit": 1,
            "is_active": True,
        },
    )
    assert coupon_response.status_code == 201, coupon_response.text

    checkout_url = (
        f"/api/v1/businesses/{test_business.id}/checkout"
    )
    checkout_payload = {
        "coupon_code": "LIMITED",
        "items": [
            {
                "service_id": service_response.json()["id"],
                "quantity": 1,
            }
        ],
    }

    first_response = client.post(
        checkout_url,
        headers=auth_headers,
        json=checkout_payload,
    )
    assert first_response.status_code == 201, first_response.text

    second_response = client.post(
        checkout_url,
        headers=auth_headers,
        json=checkout_payload,
    )
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == (
        "Coupon usage limit has been reached."
    )


def test_checkout_rejects_coupon_below_minimum_spend(
    client, test_business, auth_headers
):
    service_response = client.post(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
        json={
            "name": "Haircut",
            "price": "50.00",
            "duration_minutes": 30,
        },
    )
    assert service_response.status_code == 201, service_response.text

    coupon_response = client.post(
        f"/api/v1/businesses/{test_business.id}/coupons",
        headers=auth_headers,
        json={
            "code": "MIN100",
            "discount_type": "percentage",
            "discount_value": "10.00",
            "minimum_spend": "100.00",
            "usage_limit": 10,
            "is_active": True,
        },
    )
    assert coupon_response.status_code == 201, coupon_response.text

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/checkout",
        headers=auth_headers,
        json={
            "coupon_code": "MIN100",
            "items": [
                {
                    "service_id": service_response.json()["id"],
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Sale does not meet the coupon minimum spend."
    )


def test_checkout_rejects_invalid_coupon(
    client, test_business, auth_headers
):
    service_response = client.post(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
        json={
            "name": "Haircut",
            "price": "50.00",
            "duration_minutes": 30,
        },
    )
    assert service_response.status_code == 201, service_response.text

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/checkout",
        headers=auth_headers,
        json={
            "coupon_code": "DOESNOTEXIST",
            "items": [
                {
                    "service_id": service_response.json()["id"],
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Coupon is invalid or inactive."


def test_checkout_rejects_coupon_for_ineligible_service(
    client, test_business, auth_headers
):
    first_service_response = client.post(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
        json={
            "name": "Haircut",
            "price": "50.00",
            "duration_minutes": 30,
        },
    )
    assert first_service_response.status_code == 201, (
        first_service_response.text
    )

    second_service_response = client.post(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
        json={
            "name": "Manicure",
            "price": "40.00",
            "duration_minutes": 30,
        },
    )
    assert second_service_response.status_code == 201, (
        second_service_response.text
    )

    eligible_service_id = first_service_response.json()["id"]
    ineligible_service_id = second_service_response.json()["id"]

    coupon_response = client.post(
        f"/api/v1/businesses/{test_business.id}/coupons",
        headers=auth_headers,
        json={
            "code": "HAIRCUT10",
            "discount_type": "percentage",
            "discount_value": "10.00",
            "minimum_spend": "0.00",
            "usage_limit": 10,
            "is_active": True,
            "service_ids": [eligible_service_id],
        },
    )
    assert coupon_response.status_code == 201, coupon_response.text

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/checkout",
        headers=auth_headers,
        json={
            "coupon_code": "HAIRCUT10",
            "items": [
                {
                    "service_id": ineligible_service_id,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Coupon does not apply to the selected services."
    )