from datetime import date


def test_create_expense(client, test_business, auth_headers):
    response = client.post(
        f"/api/v1/businesses/{test_business.id}/expenses",
        headers=auth_headers,
        json={
            "category": "Supplies",
            "amount": "50000.00",
            "expense_date": str(date.today()),
            "description": "Hair products",
            "payment_method": "mobile_money",
        },
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["category"] == "Supplies"
    assert float(data["amount"]) == 50000.00
    assert data["business_id"] == str(test_business.id)


def test_list_expenses(client, test_business, auth_headers):
    url = f"/api/v1/businesses/{test_business.id}/expenses"

    client.post(
        url,
        headers=auth_headers,
        json={
            "category": "Rent",
            "amount": "200000.00",
            "expense_date": "2026-10-01",
            "payment_method": "bank_transfer",
        },
    )

    response = client.get(url, headers=auth_headers)

    assert response.status_code == 200, response.text
    expenses = response.json()
    assert len(expenses) == 1
    assert expenses[0]["category"] == "Rent"


def test_expense_requires_authentication(client, test_business):
    response = client.get(
        f"/api/v1/businesses/{test_business.id}/expenses"
    )

    assert response.status_code == 401


def test_expense_rejects_zero_amount(client, test_business, auth_headers):
    response = client.post(
        f"/api/v1/businesses/{test_business.id}/expenses",
        headers=auth_headers,
        json={
            "category": "Supplies",
            "amount": "0",
            "expense_date": "2026-10-01",
        },
    )

    assert response.status_code == 422



def test_update_expense(client, test_business, auth_headers):
    url = f"/api/v1/businesses/{test_business.id}/expenses"

    created = client.post(
        url,
        headers=auth_headers,
        json={
            "category": "Supplies",
            "amount": "50000.00",
            "expense_date": "2026-10-01",
        },
    )
    assert created.status_code == 201

    expense_id = created.json()["id"]

    response = client.patch(
        f"{url}/{expense_id}",
        headers=auth_headers,
        json={"amount": "65000.00"},
    )

    assert response.status_code == 200
    assert response.json()["amount"] == "65000.00"


def test_delete_expense(client, test_business, auth_headers):
    url = f"/api/v1/businesses/{test_business.id}/expenses"

    created = client.post(
        url,
        headers=auth_headers,
        json={
            "category": "Cleaning",
            "amount": "15000.00",
            "expense_date": "2026-10-01",
        },
    )
    assert created.status_code == 201

    expense_id = created.json()["id"]

    response = client.delete(
        f"{url}/{expense_id}",
        headers=auth_headers,
    )
    assert response.status_code == 204

    response = client.get(
        f"{url}/{expense_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404



def test_expense_summary_totals_and_categories(
    client,
    test_business,
    auth_headers,
):
    url = f"/api/v1/businesses/{test_business.id}/expenses"

    expenses = [
        {
            "category": "Supplies",
            "amount": "50000.00",
            "expense_date": "2026-10-10",
        },
        {
            "category": "Supplies",
            "amount": "25000.00",
            "expense_date": "2026-10-12",
        },
        {
            "category": "Rent",
            "amount": "200000.00",
            "expense_date": "2026-10-15",
        },
    ]

    for expense in expenses:
        response = client.post(
            url,
            headers=auth_headers,
            json=expense,
        )
        assert response.status_code == 201

    response = client.get(
        f"{url}/summary",
        headers=auth_headers,
        params={
            "start_date": "2026-10-01",
            "end_date": "2026-10-31",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert float(data["total_amount"]) == 275000.00
    assert data["expense_count"] == 3

    categories = {
        item["category"]: item
        for item in data["categories"]
    }

    assert float(categories["Supplies"]["total_amount"]) == 75000.00
    assert categories["Supplies"]["expense_count"] == 2
    assert float(categories["Rent"]["total_amount"]) == 200000.00
    assert categories["Rent"]["expense_count"] == 1
