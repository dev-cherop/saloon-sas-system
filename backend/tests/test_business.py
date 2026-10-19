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