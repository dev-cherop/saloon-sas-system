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
