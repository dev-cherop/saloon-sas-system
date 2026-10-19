import uuid
from datetime import datetime, timezone
from decimal import Decimal

from app.models.customer import Customer
from app.models.customer_visit import CustomerVisit


def create_test_customer(db_session, business_id):
    customer = Customer(
        business_id=business_id,
        first_name="Jane",
        last_name="Test",
        phone=f"+2567{uuid.uuid4().int % 10**8:08d}",
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


def test_create_customer_visit(
    client, db_session, test_business, auth_headers
):
    customer = create_test_customer(
        db_session, test_business.id
    )

    response = client.post(
        f"/api/v1/businesses/{test_business.id}"
        f"/customers/{customer.id}/visits",
        headers=auth_headers,
        json={
            "service_name": "Hair braiding",
            "amount": "50000.00",
            "visited_at": datetime.now(timezone.utc).isoformat(),
            "notes": "Customer requested medium length",
        },
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["customer_id"] == str(customer.id)
    assert data["business_id"] == str(test_business.id)
    assert data["service_name"] == "Hair braiding"
    assert Decimal(data["amount"]) == Decimal("50000.00")


def test_customer_visit_history(
    client, db_session, test_business, auth_headers
):
    customer = create_test_customer(
        db_session, test_business.id
    )

    older = CustomerVisit(
        business_id=test_business.id,
        customer_id=customer.id,
        service_name="Hair wash",
        amount=Decimal("10000.00"),
        visited_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    newer = CustomerVisit(
        business_id=test_business.id,
        customer_id=customer.id,
        service_name="Hair styling",
        amount=Decimal("20000.00"),
        visited_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    db_session.add_all([older, newer])
    db_session.commit()

    response = client.get(
        f"/api/v1/businesses/{test_business.id}"
        f"/customers/{customer.id}/visits",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 2
    assert data[0]["service_name"] == "Hair styling"
    assert data[1]["service_name"] == "Hair wash"


def test_cannot_record_visit_for_customer_in_another_business(
    client, db_session, test_business, auth_headers
):
    from app.models.business import Business

    other_business = Business(
        name="Other Salon",
        email=f"other-{uuid.uuid4()}@example.com",
    )
    db_session.add(other_business)
    db_session.commit()
    db_session.refresh(other_business)

    customer = create_test_customer(
        db_session, other_business.id
    )

    response = client.post(
        f"/api/v1/businesses/{test_business.id}"
        f"/customers/{customer.id}/visits",
        headers=auth_headers,
        json={
            "service_name": "Haircut",
            "amount": "15000.00",
        },
    )

    assert response.status_code == 404, response.text
