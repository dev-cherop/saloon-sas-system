from decimal import Decimal

from app.models.customer import Customer
from app.models.customer_visit import CustomerVisit
from app.models.loyalty_settings import LoyaltySettings


def test_earning_points_for_visit(
    client,
    db_session,
    test_business,
    auth_headers,
):
    customer = Customer(
        business_id=test_business.id,
        first_name="Loyalty",
        last_name="Test",
        phone="0700000001",
    )
    db_session.add(customer)
    db_session.flush()

    settings = LoyaltySettings(
        business_id=test_business.id,
        enabled=True,
        spend_per_point=Decimal("1000"),
        redemption_value=Decimal("1"),
        minimum_redemption_points=10,
    )
    db_session.add(settings)

    visit = CustomerVisit(
        business_id=test_business.id,
        customer_id=customer.id,
        service_name="Hair styling",
        amount=Decimal("2500.00"),
    )
    db_session.add(visit)
    db_session.commit()

    response = client.post(
        f"/api/v1/businesses/{test_business.id}"
        f"/loyalty/visits/{visit.id}/earn",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["points_change"] == 2
    assert response.json()["transaction_type"] == "earned"
    assert response.json()["customer_id"] == str(customer.id)


def test_cannot_award_points_twice_for_same_visit(
    client,
    db_session,
    test_business,
    auth_headers,
):
    customer = Customer(
        business_id=test_business.id,
        first_name="Duplicate",
        last_name="Test",
        phone="0700000002",
    )
    db_session.add(customer)
    db_session.flush()

    db_session.add(
        LoyaltySettings(
            business_id=test_business.id,
            enabled=True,
            spend_per_point=Decimal("1000"),
            redemption_value=Decimal("1"),
            minimum_redemption_points=10,
        )
    )

    visit = CustomerVisit(
        business_id=test_business.id,
        customer_id=customer.id,
        service_name="Hair treatment",
        amount=Decimal("5000.00"),
    )
    db_session.add(visit)
    db_session.commit()

    url = (
        f"/api/v1/businesses/{test_business.id}"
        f"/loyalty/visits/{visit.id}/earn"
    )

    first_response = client.post(url, headers=auth_headers)
    second_response = client.post(url, headers=auth_headers)

    assert first_response.status_code == 200, first_response.text
    assert second_response.status_code == 400, second_response.text
    assert "already awarded" in second_response.json()["detail"].lower()


def test_redeeming_loyalty_points(
    client,
    db_session,
    test_business,
    auth_headers,
):
    customer = Customer(
        business_id=test_business.id,
        first_name="Redeem",
        last_name="Test",
        phone="0700000003",
    )
    db_session.add(customer)
    db_session.flush()

    db_session.add(
        LoyaltySettings(
            business_id=test_business.id,
            enabled=True,
            spend_per_point=Decimal("1000"),
            redemption_value=Decimal("1"),
            minimum_redemption_points=10,
        )
    )

    # Seed 20 points so the customer can redeem 10.
    from app.models.loyalty_transaction import LoyaltyTransaction

    db_session.add(
        LoyaltyTransaction(
            business_id=test_business.id,
            customer_id=customer.id,
            points_change=20,
            transaction_type="earned",
            monetary_value=Decimal("0"),
            description="Test points",
        )
    )
    db_session.commit()

    response = client.post(
        f"/api/v1/businesses/{test_business.id}"
        f"/loyalty/customers/{customer.id}/redeem",
        headers=auth_headers,
        json={"points": 10},
    )

    assert response.status_code == 200, response.text
    assert response.json()["points_change"] == -10
    assert response.json()["transaction_type"] == "redeemed"



def test_get_loyalty_balance_and_history(
    client,
    db_session,
    test_business,
    auth_headers,
):
    customer = Customer(
        business_id=test_business.id,
        first_name="History",
        last_name="Test",
        phone="0700000004",
    )
    db_session.add(customer)
    db_session.flush()

    from app.models.loyalty_transaction import LoyaltyTransaction

    db_session.add_all([
        LoyaltyTransaction(
            business_id=test_business.id,
            customer_id=customer.id,
            points_change=25,
            transaction_type="earned",
            monetary_value=Decimal("0"),
            description="Points earned",
        ),
        LoyaltyTransaction(
            business_id=test_business.id,
            customer_id=customer.id,
            points_change=-10,
            transaction_type="redeemed",
            monetary_value=Decimal("10"),
            description="Points redeemed",
        ),
    ])
    db_session.commit()

    response = client.get(
        f"/api/v1/businesses/{test_business.id}"
        f"/loyalty/customers/{customer.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["balance"] == 15
    assert len(data["history"]) == 2


def test_get_loyalty_settings(
    client,
    db_session,
    test_business,
    auth_headers,
):
    response = client.get(
        f"/api/v1/businesses/{test_business.id}/loyalty/settings",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["business_id"] == str(test_business.id)
    assert data["enabled"] is True
    assert Decimal(data["spend_per_point"]) == Decimal("1000")
    assert Decimal(data["redemption_value"]) == Decimal("1")
    assert data["minimum_redemption_points"] == 10


def test_update_loyalty_settings(
    client,
    test_business,
    auth_headers,
):
    response = client.put(
        f"/api/v1/businesses/{test_business.id}/loyalty/settings",
        headers=auth_headers,
        json={
            "enabled": True,
            "spend_per_point": "500",
            "redemption_value": "2.50",
            "minimum_redemption_points": 20,
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["enabled"] is True
    assert Decimal(data["spend_per_point"]) == Decimal("500")
    assert Decimal(data["redemption_value"]) == Decimal("2.50")
    assert data["minimum_redemption_points"] == 20



def test_update_loyalty_settings_rejects_invalid_values(
    client,
    test_business,
    auth_headers,
):
    response = client.put(
        f"/api/v1/businesses/{test_business.id}/loyalty/settings",
        headers=auth_headers,
        json={
            "enabled": True,
            "spend_per_point": "0",
            "redemption_value": "1",
            "minimum_redemption_points": 10,
        },
    )

    assert response.status_code == 422, response.text
