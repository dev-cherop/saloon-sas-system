
from decimal import Decimal

from app.models.customer import Customer
from app.models.customer_visit import CustomerVisit

from datetime import date, datetime, timezone
from sqlalchemy import update
from app.models.payment import Payment

def create_visit(db_session, business_id):
    customer = Customer(
        business_id=business_id,
        first_name="Test",
        last_name="Customer",
    )
    db_session.add(customer)
    db_session.flush()

    visit = CustomerVisit(
        business_id=business_id,
        customer_id=customer.id,
        service_name="Haircut",
        amount=Decimal("50.00"),
    )
    db_session.add(visit)
    db_session.commit()
    db_session.refresh(visit)
    return visit


def test_create_payment(client, db_session, test_business, auth_headers):
    visit = create_visit(db_session, test_business.id)

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
        json={
            "visit_id": str(visit.id),
            "amount": "50.00",
            "payment_method": "cash",
            "reference": "RECEIPT-001",
            "notes": "Paid in full",
        },
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["visit_id"] == str(visit.id)
    assert data["amount"] == "50.00"
    assert data["payment_method"] == "cash"
    assert data["reference"] == "RECEIPT-001"


def test_create_payment_rejects_zero_amount(
    client, db_session, test_business, auth_headers
):
    visit = create_visit(db_session, test_business.id)

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
        json={
            "visit_id": str(visit.id),
            "amount": "0.00",
            "payment_method": "cash",
        },
    )

    assert response.status_code == 422


def test_create_payment_rejects_negative_amount(
    client, db_session, test_business, auth_headers
):
    visit = create_visit(db_session, test_business.id)

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
        json={
            "visit_id": str(visit.id),
            "amount": "-10.00",
            "payment_method": "cash",
        },
    )

    assert response.status_code == 422



def test_list_payments(client, db_session, test_business, auth_headers):
    visit = create_visit(db_session, test_business.id)

    create_response = client.post(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
        json={
            "visit_id": str(visit.id),
            "amount": "50.00",
            "payment_method": "mobile_money",
        },
    )
    assert create_response.status_code == 201, create_response.text

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1
    assert data[0]["visit_id"] == str(visit.id)
    assert data[0]["payment_method"] == "mobile_money"
    assert data[0]["amount"] == "50.00"



def test_list_payments_excludes_other_business_payments(
    client, db_session, test_business, auth_headers
):
    from app.models.business import Business

    other_business = Business(
        name="Other Salon",
        email="other@example.com",
    )
    db_session.add(other_business)
    db_session.commit()
    db_session.refresh(other_business)

    own_visit = create_visit(db_session, test_business.id)
    other_visit = create_visit(db_session, other_business.id)

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
        json={
            "visit_id": str(own_visit.id),
            "amount": "50.00",
            "payment_method": "cash",
        },
    )
    assert response.status_code == 201, response.text

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1
    assert data[0]["visit_id"] == str(own_visit.id)
    assert all(item["visit_id"] != str(other_visit.id) for item in data)


def test_create_payment_rejects_invalid_payment_method(
    client, db_session, test_business, auth_headers
):
    visit = create_visit(db_session, test_business.id)

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
        json={
            "visit_id": str(visit.id),
            "amount": "50.00",
            "payment_method": "bitcoin",
        },
    )

    assert response.status_code == 422



def test_create_payment_rejects_nonexistent_visit(
    client, test_business, auth_headers
):
    from uuid import uuid4

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
        json={
            "visit_id": str(uuid4()),
            "amount": "50.00",
            "payment_method": "cash",
        },
    )

    assert response.status_code == 404, response.text


def test_create_payment_requires_authentication(
    client, db_session, test_business
):
    visit = create_visit(db_session, test_business.id)

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/payments",
        json={
            "visit_id": str(visit.id),
            "amount": "50.00",
            "payment_method": "cash",
        },
    )

    assert response.status_code == 401, response.text


def test_payment_summary(client, db_session, test_business, auth_headers):
    visit = create_visit(db_session, test_business.id)

    for amount, method in [
        ("50.00", "cash"),
        ("75.00", "cash"),
        ("25.00", "card"),
    ]:
        response = client.post(
            f"/api/v1/businesses/{test_business.id}/payments",
            headers=auth_headers,
            json={
                "visit_id": str(visit.id),
                "amount": amount,
                "payment_method": method,
            },
        )
        assert response.status_code == 201, response.text

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payments/summary",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert float(data["total_amount"]) == 150.00
    assert data["total_count"] == 3

    by_method = {item["payment_method"]: item for item in data["by_method"]}
    assert float(by_method["cash"]["total_amount"]) == 125.00
    assert by_method["cash"]["count"] == 2
    assert float(by_method["card"]["total_amount"]) == 25.00
    assert by_method["card"]["count"] == 1





def test_payment_summary_filters_by_date(
    client, db_session, test_business, auth_headers
):
    visit = create_visit(db_session, test_business.id)

    for amount in ["40.00", "60.00"]:
        response = client.post(
            f"/api/v1/businesses/{test_business.id}/payments",
            headers=auth_headers,
            json={
                "visit_id": str(visit.id),
                "amount": amount,
                "payment_method": "cash",
            },
        )
        assert response.status_code == 201, response.text

    payments = (
        db_session.query(Payment)
        .filter(Payment.business_id == test_business.id)
        .order_by(Payment.amount)
        .all()
    )

    db_session.execute(
        update(Payment)
        .where(Payment.id == payments[0].id)
        .values(paid_at=datetime(2026, 10, 13, 12, tzinfo=timezone.utc))
    )
    db_session.execute(
        update(Payment)
        .where(Payment.id == payments[1].id)
        .values(paid_at=datetime(2026, 10, 14, 12, tzinfo=timezone.utc))
    )
    db_session.commit()

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payments/summary",
        params={"start_date": "2026-10-14", "end_date": "2026-10-14"},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert float(data["total_amount"]) == 60.00
    assert data["total_count"] == 1



def test_payment_summary_excludes_other_business(
    client, db_session, test_business, auth_headers
):
    from app.models.business import Business

    other_business = Business(
        name="Other Salon",
        email="other@example.com",
    )
    db_session.add(other_business)
    db_session.commit()
    db_session.refresh(other_business)

    own_visit = create_visit(db_session, test_business.id)
    other_visit = create_visit(db_session, other_business.id)

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
        json={
            "visit_id": str(own_visit.id),
            "amount": "40.00",
            "payment_method": "cash",
        },
    )
    assert response.status_code == 201, response.text

    # Create the other business's payment directly in the test database.
    from app.models.payment import Payment
    from decimal import Decimal

    db_session.add(
        Payment(
            business_id=other_business.id,
            visit_id=other_visit.id,
            amount=Decimal("90.00"),
            payment_method="cash",
        )
    )
    db_session.commit()

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payments/summary",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert float(data["total_amount"]) == 40.00
    assert data["total_count"] == 1



def test_payment_summary_rejects_invalid_date_range(
    client, test_business, auth_headers
):
    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payments/summary",
        params={
            "start_date": "2026-10-15",
            "end_date": "2026-10-14",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422, response.text



def test_payment_summary_requires_authentication(client, test_business):
    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payments/summary"
    )

    assert response.status_code == 401, response.text



def test_payment_summary_requires_read_permission(
    client, db_session, test_business, admin_user, auth_headers
):
    from app.models.roles import Role

    role = (
        db_session.query(Role)
        .filter(Role.id == admin_user.memberships[0].role_id)
        .first()
    )
    assert role is not None

    role.permissions = [
        permission
        for permission in role.permissions
        if permission.code != "payments:read"
    ]
    db_session.commit()

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payments/summary",
        headers=auth_headers,
    )

    assert response.status_code == 403, response.text



def test_list_payments_rejects_invalid_date_range(
    client, test_business, auth_headers
):
    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payments",
        params={
            "start_date": "2026-10-15",
            "end_date": "2026-10-14",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422, response.text



    
def test_list_payments_filters_by_visit(
    client, db_session, test_business, auth_headers
):
    visit_one = create_visit(db_session, test_business.id)
    visit_two = create_visit(db_session, test_business.id)

    for visit, amount in [
        (visit_one, "40.00"),
        (visit_two, "60.00"),
    ]:
        response = client.post(
            f"/api/v1/businesses/{test_business.id}/payments",
            headers=auth_headers,
            json={
                "visit_id": str(visit.id),
                "amount": amount,
                "payment_method": "cash",
            },
        )
        assert response.status_code == 201, response.text

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payments",
        params={"visit_id": str(visit_one.id)},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1
    assert data[0]["visit_id"] == str(visit_one.id)
    assert data[0]["amount"] == "40.00"


def test_list_payments_requires_authentication(client, test_business):
    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payments"
    )

    assert response.status_code == 401, response.text



def test_list_payments_requires_read_permission(
    client, db_session, test_business, admin_user, auth_headers
):
    from app.models.roles import Role

    role = (
        db_session.query(Role)
        .filter(Role.id == admin_user.memberships[0].role_id)
        .first()
    )
    assert role is not None

    role.permissions = [
        permission
        for permission in role.permissions
        if permission.code != "payments:read"
    ]
    db_session.commit()

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
    )

    assert response.status_code == 403, response.text


def test_create_payment_rejects_visit_from_other_business(
    client, db_session, test_business, auth_headers
):
    from app.models.business import Business

    other_business = Business(
        name="Other Salon",
        email="other@example.com",
    )
    db_session.add(other_business)
    db_session.commit()
    db_session.refresh(other_business)

    other_visit = create_visit(db_session, other_business.id)

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
        json={
            "visit_id": str(other_visit.id),
            "amount": "50.00",
            "payment_method": "cash",
        },
    )

    assert response.status_code == 404, response.text


def test_create_payment_requires_create_permission(
    client, db_session, test_business, admin_user, auth_headers
):
    from app.models.roles import Role

    visit = create_visit(db_session, test_business.id)

    role = (
        db_session.query(Role)
        .filter(Role.id == admin_user.memberships[0].role_id)
        .first()
    )
    assert role is not None

    role.permissions = [
        permission
        for permission in role.permissions
        if permission.code != "payments:create"
    ]
    db_session.commit()

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
        json={
            "visit_id": str(visit.id),
            "amount": "50.00",
            "payment_method": "cash",
        },
    )

    assert response.status_code == 403, response.text


def test_list_payments_excludes_other_business_payment(
    client, db_session, test_business, auth_headers
):
    from app.models.business import Business

    other_business = Business(
        name="Other Salon",
        email="other@example.com",
    )
    db_session.add(other_business)
    db_session.commit()
    db_session.refresh(other_business)

    own_visit = create_visit(db_session, test_business.id)
    other_visit = create_visit(db_session, other_business.id)

    own_response = client.post(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
        json={
            "visit_id": str(own_visit.id),
            "amount": "40.00",
            "payment_method": "cash",
        },
    )
    assert own_response.status_code == 201, own_response.text

    db_session.add(
        Payment(
            business_id=other_business.id,
            visit_id=other_visit.id,
            amount=Decimal("90.00"),
            payment_method="cash",
        )
    )
    db_session.commit()

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payments",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1
    assert data[0]["visit_id"] == str(own_visit.id)
    assert data[0]["amount"] == "40.00"


def test_list_payments_filters_by_date(
    client, db_session, test_business, auth_headers
):
    visit = create_visit(db_session, test_business.id)

    for amount in ["40.00", "60.00"]:
        response = client.post(
            f"/api/v1/businesses/{test_business.id}/payments",
            headers=auth_headers,
            json={
                "visit_id": str(visit.id),
                "amount": amount,
                "payment_method": "cash",
            },
        )
        assert response.status_code == 201, response.text

    payments = (
        db_session.query(Payment)
        .filter(Payment.business_id == test_business.id)
        .order_by(Payment.amount)
        .all()
    )

    db_session.execute(
        update(Payment)
        .where(Payment.id == payments[0].id)
        .values(
            paid_at=datetime(
                2026, 10, 13, 12, tzinfo=timezone.utc
            )
        )
    )
    db_session.execute(
        update(Payment)
        .where(Payment.id == payments[1].id)
        .values(
            paid_at=datetime(
                2026, 10, 14, 12, tzinfo=timezone.utc
            )
        )
    )
    db_session.commit()

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payments",
        params={
            "start_date": "2026-10-14",
            "end_date": "2026-10-14",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1
    assert data[0]["amount"] == "60.00"

