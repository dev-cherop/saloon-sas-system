import uuid


def create_test_business(client):
    response = client.post(
        "/api/v1/businesses",
        json={
            "name": "Test Salon",
            "email": "test@example.com",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_create_customer(client):
    business_id = create_test_business(client)

    response = client.post(
        f"/api/v1/businesses/{business_id}/customers",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "phone": "+256700000001",
            "email": "jane@example.com",
            "preferences": "Prefers morning appointments",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Doe"
    assert data["business_id"] == business_id


def test_search_customers(client):
    business_id = create_test_business(client)

    client.post(
        f"/api/v1/businesses/{business_id}/customers",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "phone": "+256700000001",
        },
    )

    client.post(
        f"/api/v1/businesses/{business_id}/customers",
        json={
            "first_name": "Peter",
            "last_name": "Smith",
            "phone": "+256700000002",
        },
    )

    response = client.get(
        f"/api/v1/businesses/{business_id}/customers"
        "?search=Jane"
    )

    assert response.status_code == 200

    customers = response.json()

    assert len(customers) == 1
    assert customers[0]["first_name"] == "Jane"


def test_customer_cannot_be_accessed_from_another_business(client):
    business_a = create_test_business(client)
    business_b = create_test_business(client)

    response = client.post(
        f"/api/v1/businesses/{business_a}/customers",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
        },
    )

    customer_id = response.json()["id"]

    response = client.get(
        f"/api/v1/businesses/{business_b}/customers/{customer_id}"
    )

    assert response.status_code == 404


def test_update_customer(client):
    business_id = create_test_business(client)

    response = client.post(
        f"/api/v1/businesses/{business_id}/customers",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
        },
    )

    customer_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/businesses/{business_id}/customers/{customer_id}",
        json={
            "phone": "+256700000003",
        },
    )

    assert response.status_code == 200
    assert response.json()["phone"] == "+256700000003"