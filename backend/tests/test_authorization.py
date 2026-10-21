
import uuid

from app.core.security import create_access_token, hash_password
from app.models.business import Business
from app.models.membership import BusinessMembership
from app.models.permissions import Permission
from app.models.roles import Role
from app.models.users import User


def test_business_list_contains_only_user_memberships(
    client,
    test_business,
    auth_headers,
    db_session,
):
    other_business = Business(
        name="Other Salon",
        email=f"{uuid.uuid4()}@example.com",
    )
    db_session.add(other_business)
    db_session.commit()

    response = client.get(
        "/api/v1/businesses",
        headers=auth_headers,
    )

    assert response.status_code == 200

    business_ids = {
        item["id"] for item in response.json()
    }

    assert str(test_business.id) in business_ids
    assert str(other_business.id) not in business_ids


def test_user_cannot_access_another_business(
    client,
    auth_headers,
    db_session,
):
    other_business = Business(
        name="Private Salon",
        email=f"{uuid.uuid4()}@example.com",
    )
    db_session.add(other_business)
    db_session.commit()

    response = client.get(
        f"/api/v1/businesses/{other_business.id}",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_user_cannot_list_another_business_customers(
    client,
    auth_headers,
    db_session,
):
    other_business = Business(
        name="Restricted Salon",
        email=f"{uuid.uuid4()}@example.com",
    )
    db_session.add(other_business)
    db_session.commit()

    response = client.get(
        f"/api/v1/businesses/{other_business.id}/customers",
        headers=auth_headers,
    )

    assert response.status_code == 404



def test_receptionist_cannot_manage_business_settings(
    client,
    db_session,
    test_business,
    admin_user,
):
    read_permission = db_session.query(Permission).filter_by(
        code="customers:read"
    ).one()

    receptionist_role = Role(
        name=f"RECEPTIONIST-{uuid.uuid4()}",
        description="Receptionist without settings permission",
        permissions=[read_permission],
    )
    db_session.add(receptionist_role)
    db_session.flush()

    receptionist = User(
        email=f"receptionist-{uuid.uuid4()}@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="Test",
        last_name="Receptionist",
        is_active=True,
    )
    db_session.add(receptionist)
    db_session.flush()

    membership = BusinessMembership(
        user_id=receptionist.id,
        business_id=test_business.id,
        role_id=receptionist_role.id,
    )
    db_session.add(membership)
    db_session.commit()

    token = create_access_token(receptionist.id)

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/branches",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403

def test_auth_context_returns_system_permissions(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["system_permissions"] == []


def test_auth_context_returns_assigned_system_permissions(
    client,
    auth_headers,
    admin_user,
    db_session,
):
    from app.models.system_permissions import (
        SystemPermission,
        SystemRole,
    )

    permission = SystemPermission(
        code="system:businesses:create",
        description="Create businesses on the platform",
    )
    role = SystemRole(
        name=f"Test System Admin {uuid.uuid4()}",
        permissions=[permission],
    )
    db_session.add(role)
    db_session.flush()
    admin_user.system_roles.append(role)
    db_session.commit()

    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert "system:businesses:create" in response.json()["system_permissions"]
