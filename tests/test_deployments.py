def test_list_deployments_filters_by_status(client, admin_headers, sample_timestamp):
    client.post(
        "/api/v1/deployments",
        headers=admin_headers,
        json={
            "service": "payments",
            "version": "1.2.0",
            "environment": "staging",
            "status": "running",
            "deployed_at": sample_timestamp.isoformat(),
        },
    )
    client.post(
        "/api/v1/deployments",
        headers=admin_headers,
        json={
            "service": "payments",
            "version": "1.2.1",
            "environment": "staging",
            "status": "failed",
            "deployed_at": sample_timestamp.isoformat(),
        },
    )

    response = client.get("/api/v1/deployments?status=running", headers=admin_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert len(payload["items"]) == 1
    assert payload["items"][0]["status"] == "running"
