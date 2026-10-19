def test_create_service(client, test_business, auth_headers):
    response = client.post(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
        json={
            "name": "Haircut",
            "description": "Standard haircut",
            "price": "25.00",
            "duration_minutes": 30,
        },
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Haircut"
    assert data["description"] == "Standard haircut"
    assert data["price"] == "25.00"
    assert data["duration_minutes"] == 30
    assert data["is_active"] is True
    assert data["business_id"] == str(test_business.id)


def test_create_service_rejects_negative_price(
    client, test_business, auth_headers
):
    response = client.post(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
        json={
            "name": "Haircut",
            "price": "-10.00",
            "duration_minutes": 30,
        },
    )

    assert response.status_code == 422


def test_create_service_rejects_invalid_duration(
    client, test_business, auth_headers
):
    response = client.post(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
        json={
            "name": "Haircut",
            "price": "25.00",
            "duration_minutes": 0,
        },
    )

    assert response.status_code == 422


def test_list_services(client, test_business, auth_headers):
    create_response = client.post(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
        json={
            "name": "Haircut",
            "price": "25.00",
            "duration_minutes": 30,
        },
    )
    assert create_response.status_code == 201, create_response.text

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Haircut"


def test_service_is_isolated_by_business(
    client, db_session, test_business, auth_headers
):
    from app.models.business import Business

    create_response = client.post(
        f"/api/v1/businesses/{test_business.id}/services",
        headers=auth_headers,
        json={
            "name": "Haircut",
            "price": "25.00",
            "duration_minutes": 30,
        },
    )
    assert create_response.status_code == 201, create_response.text
    service_id = create_response.json()["id"]

    other_business = Business(
        name="Other Salon",
        email="other-services@example.com",
    )
    db_session.add(other_business)
    db_session.commit()
    db_session.refresh(other_business)

    response = client.get(
        f"/api/v1/businesses/{other_business.id}/services/{service_id}",
        headers=auth_headers,
    )

    assert response.status_code == 404, response.text


def test_user_without_services_read_permission_gets_403(
    client,
    db_session,
    test_business,
    admin_user,
):
    import uuid

    from app.core.security import create_access_token, hash_password
    from app.models.membership import BusinessMembership
    from app.models.permissions import Permission
    from app.models.roles import Role
    from app.models.users import User

    read_permission = db_session.query(Permission).filter_by(
        code="customers:read"
    ).one()

    role = Role(
        name=f"NO_SERVICES_READ-{uuid.uuid4()}",
        description="Cannot read services",
        permissions=[read_permission],
    )
    db_session.add(role)
    db_session.flush()

    user = User(
        email=f"no-services-{uuid.uuid4()}@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="Test",
        last_name="User",
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

    token = create_access_token(user.id)

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/services",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403, response.text