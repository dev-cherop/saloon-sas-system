
import uuid

from datetime import date

from app.models.business import Business
from app.models.permissions import Permission
from app.models.roles import Role
from app.models.membership import BusinessMembership
from app.models.users import User
from app.core.security import create_access_token, hash_password


def create_worker(client, business_id, auth_headers):
    response = client.post(
        f"/api/v1/businesses/{business_id}/workers",
        headers=auth_headers,
        json={"first_name": "Jane", "last_name": "Doe"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_payroll(client, business_id, worker_id, auth_headers, **overrides):
    payload = {
        "worker_id": worker_id,
        "period_start": "2026-10-01",
        "period_end": "2026-10-31",
        "base_pay": "1000000.00",
        "commission": "150000.00",
        "bonus": "50000.00",
        "deductions": "100000.00",
    }
    payload.update(overrides)
    return client.post(
        f"/api/v1/businesses/{business_id}/payroll",
        headers=auth_headers,
        json=payload,
    )


def test_create_payroll_calculates_net_pay(
    client, test_business, auth_headers
):
    worker_id = create_worker(client, test_business.id, auth_headers)

    response = create_payroll(
        client, test_business.id, worker_id, auth_headers
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["worker_id"] == worker_id
    assert data["net_pay"] == "1100000.00"
    assert data["status"] == "draft"
    assert data["payment_method"] is None
    assert data["paid_at"] is None


def test_create_payroll_defaults_optional_amounts_to_zero(
    client, test_business, auth_headers
):
    worker_id = create_worker(client, test_business.id, auth_headers)

    response = create_payroll(
        client,
        test_business.id,
        worker_id,
        auth_headers,
        commission="0",
        bonus="0",
        deductions="0",
    )

    assert response.status_code == 201, response.text
    assert response.json()["net_pay"] == "1000000.00"


def test_create_payroll_rejects_invalid_period(
    client, test_business, auth_headers
):
    worker_id = create_worker(client, test_business.id, auth_headers)

    response = create_payroll(
        client,
        test_business.id,
        worker_id,
        auth_headers,
        period_start="2026-11-01",
        period_end="2026-10-01",
    )

    assert response.status_code == 422


def test_create_payroll_rejects_negative_amount(
    client, test_business, auth_headers
):
    worker_id = create_worker(client, test_business.id, auth_headers)

    response = create_payroll(
        client,
        test_business.id,
        worker_id,
        auth_headers,
        base_pay="-100",
    )

    assert response.status_code == 422


def test_create_payroll_rejects_worker_from_another_business(
    client, db_session, test_business, auth_headers
):
    other_business = Business(name="Other Salon")
    db_session.add(other_business)
    db_session.commit()
    db_session.refresh(other_business)

    worker_id = create_worker(client, test_business.id, auth_headers)

    response = create_payroll(
        client, other_business.id, worker_id, auth_headers
    )

    # The authenticated user has no membership in the other business.
    assert response.status_code in (403, 404)


def test_create_payroll_rejects_duplicate_period(
    client, test_business, auth_headers
):
    worker_id = create_worker(client, test_business.id, auth_headers)

    first = create_payroll(
        client, test_business.id, worker_id, auth_headers
    )
    assert first.status_code == 201, first.text

    second = create_payroll(
        client, test_business.id, worker_id, auth_headers
    )
    assert second.status_code == 409, second.text


def test_list_payroll_records(
    client, test_business, auth_headers
):
    worker_id = create_worker(client, test_business.id, auth_headers)
    created = create_payroll(
        client, test_business.id, worker_id, auth_headers
    )
    assert created.status_code == 201, created.text

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payroll",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1
    assert response.json()[0]["worker_id"] == worker_id


def test_update_draft_payroll_recalculates_net_pay(
    client, test_business, auth_headers
):
    worker_id = create_worker(client, test_business.id, auth_headers)
    created = create_payroll(
        client, test_business.id, worker_id, auth_headers
    )
    assert created.status_code == 201, created.text
    payroll_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/businesses/{test_business.id}/payroll/{payroll_id}",
        headers=auth_headers,
        json={"base_pay": "1200000", "deductions": "200000"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["net_pay"] == "1200000.00"


def test_approve_then_pay_payroll(
    client, test_business, auth_headers
):
    worker_id = create_worker(client, test_business.id, auth_headers)
    created = create_payroll(
        client, test_business.id, worker_id, auth_headers
    )
    assert created.status_code == 201, created.text
    payroll_id = created.json()["id"]
    url = (
        f"/api/v1/businesses/{test_business.id}/payroll/"
        f"{payroll_id}/status"
    )

    approved = client.patch(
        url,
        headers=auth_headers,
        json={"status": "approved"},
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "approved"

    paid = client.patch(
        url,
        headers=auth_headers,
        json={"status": "paid", "payment_method": "mobile_money"},
    )
    assert paid.status_code == 200, paid.text
    assert paid.json()["status"] == "paid"
    assert paid.json()["payment_method"] == "mobile_money"
    assert paid.json()["paid_at"] is not None


def test_cannot_pay_without_payment_method(
    client, test_business, auth_headers
):
    worker_id = create_worker(client, test_business.id, auth_headers)
    created = create_payroll(
        client, test_business.id, worker_id, auth_headers
    )
    assert created.status_code == 201, created.text
    payroll_id = created.json()["id"]
    url = (
        f"/api/v1/businesses/{test_business.id}/payroll/"
        f"{payroll_id}/status"
    )

    approved = client.patch(
        url, headers=auth_headers, json={"status": "approved"}
    )
    assert approved.status_code == 200, approved.text

    paid = client.patch(
        url, headers=auth_headers, json={"status": "paid"}
    )
    assert paid.status_code == 422


def test_cannot_edit_approved_payroll(
    client, test_business, auth_headers
):
    worker_id = create_worker(client, test_business.id, auth_headers)
    created = create_payroll(
        client, test_business.id, worker_id, auth_headers
    )
    assert created.status_code == 201, created.text
    payroll_id = created.json()["id"]

    approved = client.patch(
        f"/api/v1/businesses/{test_business.id}/payroll/"
        f"{payroll_id}/status",
        headers=auth_headers,
        json={"status": "approved"},
    )
    assert approved.status_code == 200, approved.text

    response = client.patch(
        f"/api/v1/businesses/{test_business.id}/payroll/{payroll_id}",
        headers=auth_headers,
        json={"base_pay": "2000000"},
    )
    assert response.status_code == 409


def test_payroll_requires_authentication(client, test_business):
    response = client.get(
        f"/api/v1/businesses/{test_business.id}/payroll"
    )
    assert response.status_code == 401


def test_payroll_requires_permission(
    client, db_session, test_business
):
    permission = Permission(
        code="payroll:read",
        description="View worker payroll records",
    )
    db_session.add(permission)
    db_session.flush()

    role = Role(
        name=f"PAYROLL-READ-{uuid.uuid4()}",
        description="Payroll read only",
        permissions=[permission],
    )
    db_session.add(role)
    db_session.flush()

    user = User(
        email=f"payroll-reader-{uuid.uuid4()}@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="Payroll",
        last_name="Reader",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    db_session.add(
        BusinessMembership(
            user_id=user.id,
            business_id=test_business.id,
            role_id=role.id,
        )
    )
    db_session.commit()

    headers = {
        "Authorization": f"Bearer {create_access_token(user.id)}"
    }

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/payroll",
        headers=headers,
        json={
            "worker_id": str(uuid.uuid4()),
            "period_start": "2026-10-01",
            "period_end": "2026-10-31",
            "base_pay": "1000000",
        },
    )
    assert response.status_code == 403
