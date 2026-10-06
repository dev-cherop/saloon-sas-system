
def test_create_business(client):
    response = client.post(
        "/api/v1/businesses",
        json={
            "name": "Urban Glow Salon",
            "email": "admin@example.com",
            "phone": "+256700000000",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Urban Glow Salon"
    assert data["is_active"] is True
    assert "id" in data


def test_create_and_list_branches(client):
    business_response = client.post(
        "/api/v1/businesses",
        json={"name": "Urban Glow Salon"},
    )
    business_id = business_response.json()["id"]

    create_response = client.post(
        f"/api/v1/businesses/{business_id}/branches",
        json={
            "name": "Kampala Central",
            "address": "Kampala, Uganda",
        },
    )

    assert create_response.status_code == 201
    assert create_response.json()["business_id"] == business_id

    list_response = client.get(
        f"/api/v1/businesses/{business_id}/branches"
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["name"] == "Kampala Central"


def test_branch_requires_existing_business(client):
    import uuid

    missing_business_id = uuid.uuid4()

    response = client.post(
        f"/api/v1/businesses/{missing_business_id}/branches",
        json={"name": "Orphan Branch"},
    )

    assert response.status_code == 404


def test_invalid_business_name_is_rejected(client):
    response = client.post(
        "/api/v1/businesses",
        json={"name": "X"},
    )

    assert response.status_code == 422