from app.models.business import Business

def test_get_business(
    client,
    test_business,
    auth_headers,
):
    response = client.get(
        f"/api/v1/businesses/{test_business.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(test_business.id)
    assert data["name"] == "Test Salon"


def test_create_and_list_branches(
    client,
    test_business,
    auth_headers,
):
    create_response = client.post(
        f"/api/v1/businesses/{test_business.id}/branches",
        headers=auth_headers,
        json={
            "name": "Kampala Central",
            "address": "Kampala, Uganda",
        },
    )

    assert create_response.status_code == 201

    data = create_response.json()

    assert data["business_id"] == str(test_business.id)
    assert data["name"] == "Kampala Central"

    list_response = client.get(
        f"/api/v1/businesses/{test_business.id}/branches",
        headers=auth_headers,
    )

    assert list_response.status_code == 200

    branches = list_response.json()

    assert len(branches) == 1
    assert branches[0]["name"] == "Kampala Central"




def test_update_branch(client, test_business, auth_headers):
    create_response = client.post(
        f"/api/v1/businesses/{test_business.id}/branches",
        headers=auth_headers,
        json={"name": "Kampala Central", "address": "Old address"},
    )
    assert create_response.status_code == 201
    branch_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/businesses/{test_business.id}/branches/{branch_id}",
        headers=auth_headers,
        json={"name": "Kampala North", "address": "New address"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Kampala North"
    assert response.json()["address"] == "New address"
    assert response.json()["is_active"] is True


def test_deactivate_branch(client, test_business, auth_headers):
    create_response = client.post(
        f"/api/v1/businesses/{test_business.id}/branches",
        headers=auth_headers,
        json={"name": "Kampala Central"},
    )
    assert create_response.status_code == 201
    branch_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/businesses/{test_business.id}/branches/{branch_id}",
        headers=auth_headers,
        json={"is_active": False},
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_update_branch_rejects_different_business(
    client, db_session, test_business, auth_headers
):
    create_response = client.post(
        f"/api/v1/businesses/{test_business.id}/branches",
        headers=auth_headers,
        json={"name": "Kampala Central"},
    )
    assert create_response.status_code == 201
    branch_id = create_response.json()["id"]

    other_business = Business(name="Other Salon")
    db_session.add(other_business)
    db_session.commit()
    db_session.refresh(other_business)

    response = client.patch(
        f"/api/v1/businesses/{other_business.id}/branches/{branch_id}",
        headers=auth_headers,
        json={"name": "Unauthorized Change"},
    )

    assert response.status_code == 404


def test_business_admin_cannot_create_business_without_system_permission(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/businesses",
        headers=auth_headers,
        json={
            "name": "Unauthorized Salon",
            "email": "unauthorized@example.com",
        },
    )

    assert response.status_code == 403


def test_system_permission_allows_business_creation(
    client,
    db_session,
    admin_user,
    auth_headers,
):
    from app.models.membership import BusinessMembership
    from app.models.roles import Role
    from app.models.system_permissions import SystemPermission, SystemRole
    from app.models.users import User

    permission = SystemPermission(
        code="system:businesses:create",
        description="Create businesses on the platform",
    )
    role = SystemRole(
        name="Test System Administrator",
        description="Test-only system role",
        permissions=[permission],
    )
    db_session.add(role)
    db_session.flush()
    admin_user.system_roles.append(role)

    salon_owner = User(
        email="salon-owner@example.com",
        password_hash="test-password-hash",
        first_name="Salon",
        last_name="Owner",
        is_active=True,
    )
    business_admin_role = Role(
        name="ADMIN",
        description="Business administrator",
    )
    db_session.add_all([salon_owner, business_admin_role])
    db_session.commit()
    db_session.refresh(salon_owner)

    response = client.post(
        "/api/v1/businesses",
        headers=auth_headers,
        json={
            "name": "New Salon",
            "email": "new@example.com",
            "admin_email": salon_owner.email,
        },
    )

    assert response.status_code == 201, response.json()
    assert response.json()["name"] == "New Salon"
    assert response.json()["email"] == "new@example.com"

    membership = db_session.query(BusinessMembership).filter_by(
        user_id=salon_owner.id,
    ).one()
    assert str(membership.business_id) == response.json()["id"]
    assert membership.role.name == "ADMIN"
    assert salon_owner.system_roles == []


def test_business_settings_rejects_user_from_another_business(
    client,
    db_session,
    test_business,
    auth_headers,
):
    other_business = Business(name="Other Salon")
    db_session.add(other_business)
    db_session.commit()
    db_session.refresh(other_business)

    response = client.get(
        f"/api/v1/businesses/{other_business.id}",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Business not found"