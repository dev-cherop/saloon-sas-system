import uuid

from app.models.business import Business


BASE_URL = "/api/v1/businesses/{business_id}/coupons"


def coupon_payload(**overrides):
    payload = {
        "code": "WELCOME10",
        "description": "Welcome discount",
        "discount_type": "percentage",
        "discount_value": "10.00",
        "minimum_spend": "0.00",
        "usage_limit": 100,
        "is_active": True,
    }
    payload.update(overrides)
    return payload


def test_create_coupon(client, test_business, auth_headers):
    response = client.post(
        BASE_URL.format(business_id=test_business.id),
        headers=auth_headers,
        json=coupon_payload(),
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["code"] == "WELCOME10"
    assert data["discount_type"] == "percentage"
    assert data["usage_count"] == 0


def test_list_coupons(client, test_business, auth_headers):
    url = BASE_URL.format(business_id=test_business.id)
    created = client.post(
        url, headers=auth_headers, json=coupon_payload()
    )
    assert created.status_code == 201, created.text

    response = client.get(url, headers=auth_headers)

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1


def test_update_coupon(client, test_business, auth_headers):
    url = BASE_URL.format(business_id=test_business.id)
    created = client.post(
        url, headers=auth_headers, json=coupon_payload()
    )
    assert created.status_code == 201, created.text

    response = client.patch(
        f"{url}/{created.json()['id']}",
        headers=auth_headers,
        json={"description": "Updated discount", "discount_value": "15.00"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["description"] == "Updated discount"
    assert float(response.json()["discount_value"]) == 15.0


def test_delete_coupon(client, test_business, auth_headers):
    url = BASE_URL.format(business_id=test_business.id)
    created = client.post(
        url, headers=auth_headers, json=coupon_payload()
    )
    assert created.status_code == 201, created.text
    coupon_id = created.json()["id"]

    response = client.delete(f"{url}/{coupon_id}", headers=auth_headers)

    assert response.status_code == 204
    assert client.get(
        f"{url}/{coupon_id}", headers=auth_headers
    ).status_code == 404


def test_coupon_code_is_normalized(client, test_business, auth_headers):
    response = client.post(
        BASE_URL.format(business_id=test_business.id),
        headers=auth_headers,
        json=coupon_payload(code="  welcome10  "),
    )

    assert response.status_code == 201, response.text
    assert response.json()["code"] == "WELCOME10"


def test_percentage_discount_cannot_exceed_100(
    client, test_business, auth_headers
):
    response = client.post(
        BASE_URL.format(business_id=test_business.id),
        headers=auth_headers,
        json=coupon_payload(discount_value="101.00"),
    )

    assert response.status_code == 422, response.text


def test_expiry_must_follow_start_date(client, test_business, auth_headers):
    response = client.post(
        BASE_URL.format(business_id=test_business.id),
        headers=auth_headers,
        json=coupon_payload(
            starts_at="2026-11-10T10:00:00Z",
            expires_at="2026-11-09T10:00:00Z",
        ),
    )

    assert response.status_code == 422, response.text


def test_coupon_requires_authentication(client, test_business):
    response = client.get(
        BASE_URL.format(business_id=test_business.id)
    )

    assert response.status_code == 401


def test_coupon_cannot_be_accessed_from_another_business(
    client, db_session, test_business, auth_headers
):
    url = BASE_URL.format(business_id=test_business.id)
    created = client.post(
        url, headers=auth_headers, json=coupon_payload()
    )
    assert created.status_code == 201, created.text

    other_business = Business(
        name="Other Salon",
        email=f"other-{uuid.uuid4()}@example.com",
    )
    db_session.add(other_business)
    db_session.commit()
    db_session.refresh(other_business)

    other_url = BASE_URL.format(business_id=other_business.id)
    response = client.get(
        f"{other_url}/{created.json()['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_coupon_read_requires_permission(
    client, db_session, test_business
):
    from app.core.security import create_access_token, hash_password
    from app.models.membership import BusinessMembership
    from app.models.roles import Role
    from app.models.users import User

    role = Role(
        name=f"NO-COUPONS-{uuid.uuid4()}",
        description="Role without coupon access",
        permissions=[],
    )
    user = User(
        email=f"no-coupons-{uuid.uuid4()}@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="No",
        last_name="Coupons",
        is_active=True,
    )
    db_session.add_all([role, user])
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
        BASE_URL.format(business_id=test_business.id),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403, response.text


def test_update_coupon_rejects_percentage_over_100(
    client, test_business, auth_headers
):
    url = BASE_URL.format(business_id=test_business.id)
    created = client.post(
        url,
        headers=auth_headers,
        json=coupon_payload(
            code="FIXED150",
            discount_type="fixed",
            discount_value="150.00",
        ),
    )
    assert created.status_code == 201, created.text

    response = client.patch(
        f"{url}/{created.json()['id']}",
        headers=auth_headers,
        json={"discount_type": "percentage"},
    )

    assert response.status_code == 422, response.text
