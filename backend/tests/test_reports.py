def test_reports_requires_authentication(client, test_business):
    response = client.get(
        f"/api/v1/businesses/{test_business.id}/reports/summary",
        params={
            "start_date": "2026-10-01",
            "end_date": "2026-10-31",
        },
    )

    assert response.status_code == 401