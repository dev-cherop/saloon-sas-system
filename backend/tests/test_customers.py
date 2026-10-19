def test_create_customer(
    client,
    test_business,
    auth_headers,
):
    response = client.post(
        f"/api/v1/businesses/{test_business.id}/customers",
        headers=auth_headers,
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
    assert data["business_id"] == str(test_business.id)


def test_search_customers(
    client,
    test_business,
    auth_headers,
):
    client.post(
        f"/api/v1/businesses/{test_business.id}/customers",
        headers=auth_headers,
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "phone": "+256700000001",
        },
    )

    client.post(
        f"/api/v1/businesses/{test_business.id}/customers",
        headers=auth_headers,
        json={
            "first_name": "Peter",
            "last_name": "Smith",
            "phone": "+256700000002",
        },
    )

    response = client.get(
        f"/api/v1/businesses/{test_business.id}/customers",
        headers=auth_headers,
        params={"search": "Jane"},
    )

    assert response.status_code == 200

    customers = response.json()

    assert len(customers) == 1
    assert customers[0]["first_name"] == "Jane"



def test_customer_cannot_be_accessed_from_another_business(
    client,
    db_session,
    test_business,
    auth_headers,
):
    from app.models.business import Business

    business_b = Business(
        name="Another Salon",
    )

    db_session.add(business_b)
    db_session.commit()
    db_session.refresh(business_b)

    response = client.post(
        f"/api/v1/businesses/{test_business.id}/customers",
        headers=auth_headers,
        json={
            "first_name": "Jane",
            "last_name": "Doe",
        },
    )

    assert response.status_code == 201

    customer_id = response.json()["id"]

    response = client.get(
        f"/api/v1/businesses/{business_b.id}/customers/{customer_id}",
        headers=auth_headers,
    )

    # User isn't a member of business B.
    assert response.status_code == 404


def test_customer_requires_authentication(
    client,
    test_business,
):
    response = client.get(
        f"/api/v1/businesses/{test_business.id}/customers",
    )

    assert response.status_code == 401


def test_customer_requires_authentication(
    client,
    test_business,
):
    response = client.get(
        f"/api/v1/businesses/{test_business.id}/customers",
    )

    assert response.status_code == 401