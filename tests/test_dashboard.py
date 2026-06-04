def test_dashboard_summary(client, admin_headers, sample_timestamp):
    client.post(
        "/api/v1/servers",
        headers=admin_headers,
        json={
            "name": "worker-staging-1",
            "environment": "staging",
            "ip_address": "10.0.0.20",
            "cpu_usage": 12.1,
            "memory_usage": 45.0,
            "status": "running",
        },
    )
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
        "/api/v1/incidents",
        headers=admin_headers,
        json={
            "title": "Staging API degradation",
            "description": "Elevated error rates on staging",
            "severity": "medium",
            "status": "open",
            "timeline": [{"message": "Alert triggered", "occurred_at": sample_timestamp.isoformat()}],
        },
    )
    client.post(
        "/api/v1/uptime",
        headers=admin_headers,
        json={
            "name": "Public API",
            "url": "https://api.example.com/health",
            "environment": "production",
            "checks": [{"response_time_ms": 180.0, "is_available": True, "checked_at": sample_timestamp.isoformat()}],
            "downtime_events": [],
        },
    )

    response = client.get("/api/v1/dashboard/summary", headers=admin_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_servers"] == 1
    assert payload["active_deployments"] == 1
    assert payload["open_incidents"] == 1
    assert payload["uptime_percentage"] == 100.0
    assert payload["environment_overview"]["staging"] == 1
