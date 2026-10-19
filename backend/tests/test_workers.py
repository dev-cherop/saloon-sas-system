from app.models.business import Business
import uuid

from app.core.security import create_access_token, hash_password
from app.models.business import Business
from app.models.membership import BusinessMembership
from app.models.permissions import Permission
from app.models.roles import Role
from app.models.users import User

def test_create_worker(client, test_business, auth_headers):
    response = client.post(
        f"/api/v1/businesses/{test_business.id}/workers",
        headers=auth_headers,
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "phone": "0700123456",
            "email": "jane@example.com",
            "specialty": "Hair Stylist",
        },
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Doe"
    assert data["business_id"] == str(test_business.id)
    assert data["is_active"] is True

    
def test_list_workers(client, test_business, auth_headers):
    for first_name in ["Jane", "Alice"]:
        response = client.post(
            f"/api/v1/businesses/{test_business.id}/workers",
            headers=auth_headers,
            json={
                "first_name": first_name,
                "last_name": "Doe",
            },
        )
        assert response.status_code == 201, response.text

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/workers",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 2
    assert [worker["first_name"] for worker in data] == ["Alice", "Jane"]


def test_update_worker(client, test_business, auth_headers):
    create_response = client.post(
        f"/api/v1/businesses/{test_business.id}/workers",
        headers=auth_headers,
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "specialty": "Braiding",
        },
    )
    assert create_response.status_code == 201, create_response.text
    worker_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/businesses/{test_business.id}/workers/{worker_id}",
        headers=auth_headers,
        json={"specialty": "Hair Coloring"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["specialty"] == "Hair Coloring"



def test_worker_cannot_be_accessed_by_another_business(
    client, db_session, test_business, auth_headers
):
    create_response = client.post(
        f"/api/v1/businesses/{test_business.id}/workers",
        headers=auth_headers,
        json={"first_name": "Jane", "last_name": "Doe"},
    )
    assert create_response.status_code == 201, create_response.text
    worker_id = create_response.json()["id"]

    other_business = Business(name="Other Salon")
    db_session.add(other_business)
    db_session.commit()
    db_session.refresh(other_business)

    response = client.get(
        f"/api/v1/businesses/{other_business.id}/workers/{worker_id}",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_delete_worker(client, test_business, auth_headers):
    create_response = client.post(
        f"/api/v1/businesses/{test_business.id}/workers",
        headers=auth_headers,
        json={"first_name": "Jane", "last_name": "Doe"},
    )
    assert create_response.status_code == 201, create_response.text
    worker_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/businesses/{test_business.id}/workers/{worker_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/businesses/{test_business.id}/workers/{worker_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404



def test_create_worker_requires_authentication(client, test_business):
    response = client.post(
        f"/api/v1/businesses/{test_business.id}/workers",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
        },
    )

    assert response.status_code == 401


def test_create_worker_without_permission_returns_403(
    client, db_session, test_business
):
    read_permission = Permission(
        code="workers:read",
        description="View workers",
    )
    db_session.add(read_permission)
    db_session.flush()

    role = Role(
        name=f"RESTRICTED-{uuid.uuid4()}",
        description="Worker read access only",
        permissions=[read_permission],
    )
    db_session.add(role)
    db_session.flush()

    user = User(
        email=f"restricted-{uuid.uuid4()}@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="Restricted",
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

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={"first_name": "Jane", "last_name": "Doe"},
    )

    assert response.status_code == 403
