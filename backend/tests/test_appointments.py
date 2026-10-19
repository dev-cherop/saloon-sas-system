from datetime import datetime, timedelta, timezone


def create_appointment_dependencies(client, test_business, auth_headers):
    base_url = f"/api/v1/businesses/{test_business.id}"

    customer_response = client.post(
        f"{base_url}/customers",
        headers=auth_headers,
        json={"first_name": "Jane", "last_name": "Doe"},
    )
    assert customer_response.status_code == 201, customer_response.text

    service_response = client.post(
        f"{base_url}/services",
        headers=auth_headers,
        json={
            "name": "Hair Styling",
            "price": "15000.00",
            "duration_minutes": 60,
        },
    )
    assert service_response.status_code == 201, service_response.text

    worker_response = client.post(
        f"{base_url}/workers",
        headers=auth_headers,
        json={"first_name": "Alice", "last_name": "Stylist"},
    )
    assert worker_response.status_code == 201, worker_response.text

    return (
        base_url,
        customer_response.json()["id"],
        service_response.json()["id"],
        worker_response.json()["id"],
    )


def appointment_payload(customer_id, service_id, worker_id, start_time=None):
    start = start_time or (
        datetime.now(timezone.utc) + timedelta(days=2)
    ).replace(hour=10, minute=0, second=0, microsecond=0)

    return {
        "customer_id": customer_id,
        "service_id": service_id,
        "worker_id": worker_id,
        "start_time": start.isoformat(),
        "end_time": (start + timedelta(minutes=60)).isoformat(),
        "notes": "Appointment test",
    }


def test_create_appointment(client, test_business, auth_headers):
    base_url, customer_id, service_id, worker_id = (
        create_appointment_dependencies(client, test_business, auth_headers)
    )

    response = client.post(
        f"{base_url}/appointments",
        headers=auth_headers,
        json=appointment_payload(customer_id, service_id, worker_id),
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["customer_id"] == customer_id
    assert data["service_id"] == service_id
    assert data["worker_id"] == worker_id
    assert data["business_id"] == str(test_business.id)
    assert data["status"] == "scheduled"


def test_list_appointments(client, test_business, auth_headers):
    base_url, customer_id, service_id, worker_id = (
        create_appointment_dependencies(client, test_business, auth_headers)
    )

    create_response = client.post(
        f"{base_url}/appointments",
        headers=auth_headers,
        json=appointment_payload(customer_id, service_id, worker_id),
    )
    assert create_response.status_code == 201, create_response.text

    response = client.get(
        f"{base_url}/appointments",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1


def test_worker_cannot_have_overlapping_appointments(
    client, test_business, auth_headers
):
    base_url, customer_id, service_id, worker_id = (
        create_appointment_dependencies(client, test_business, auth_headers)
    )

    start = (
        datetime.now(timezone.utc) + timedelta(days=3)
    ).replace(hour=11, minute=0, second=0, microsecond=0)

    first_response = client.post(
        f"{base_url}/appointments",
        headers=auth_headers,
        json=appointment_payload(
            customer_id, service_id, worker_id, start
        ),
    )
    assert first_response.status_code == 201, first_response.text

    second_response = client.post(
        f"{base_url}/appointments",
        headers=auth_headers,
        json=appointment_payload(
            customer_id, service_id, worker_id, start + timedelta(minutes=30)
        ),
    )

    assert second_response.status_code == 409, second_response.text


def test_create_appointment_requires_authentication(client, test_business):
    response = client.post(
        f"/api/v1/businesses/{test_business.id}/appointments",
        json={},
    )

    assert response.status_code == 401


def test_appointment_cannot_be_accessed_by_another_business(
    client, db_session, test_business, auth_headers
):
    from app.models.business import Business

    base_url, customer_id, service_id, worker_id = (
        create_appointment_dependencies(client, test_business, auth_headers)
    )

    create_response = client.post(
        f"{base_url}/appointments",
        headers=auth_headers,
        json=appointment_payload(customer_id, service_id, worker_id),
    )
    assert create_response.status_code == 201, create_response.text
    appointment_id = create_response.json()["id"]

    other_business = Business(name="Other Salon")
    db_session.add(other_business)
    db_session.commit()
    db_session.refresh(other_business)

    response = client.get(
        f"/api/v1/businesses/{other_business.id}/appointments/{appointment_id}",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_list_appointments_requires_read_permission(
    client, test_business, auth_headers, db_session, admin_user
):
    from app.models.roles import Role
    from app.models.permissions import Permission

    membership = admin_user.memberships[0]
    role = membership.role

    read_permission = next(
        (
            permission
            for permission in role.permissions
            if permission.code == "appointments:read"
        ),
        None,
    )

    if read_permission:
        role.permissions.remove(read_permission)
        db_session.commit()

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/appointments",
        headers=auth_headers,
    )

    assert response.status_code == 403



def test_update_appointment(client, test_business, auth_headers):
    base_url, customer_id, service_id, worker_id = (
        create_appointment_dependencies(client, test_business, auth_headers)
    )

    create_response = client.post(
        f"{base_url}/appointments",
        headers=auth_headers,
        json=appointment_payload(customer_id, service_id, worker_id),
    )
    assert create_response.status_code == 201, create_response.text

    appointment_id = create_response.json()["id"]

    response = client.patch(
        f"{base_url}/appointments/{appointment_id}",
        headers=auth_headers,
        json={"notes": "Updated appointment notes"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["notes"] == "Updated appointment notes"



def test_delete_appointment(client, test_business, auth_headers):
    base_url, customer_id, service_id, worker_id = (
        create_appointment_dependencies(client, test_business, auth_headers)
    )

    create_response = client.post(
        f"{base_url}/appointments",
        headers=auth_headers,
        json=appointment_payload(customer_id, service_id, worker_id),
    )
    assert create_response.status_code == 201, create_response.text

    appointment_id = create_response.json()["id"]

    response = client.delete(
        f"{base_url}/appointments/{appointment_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    get_response = client.get(
        f"{base_url}/appointments/{appointment_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404
