def test_server_crud(client, admin_headers):
    create_response = client.post(
        "/api/v1/servers",
        headers=admin_headers,
        json={
            "name": "api-prod-1",
            "environment": "production",
            "ip_address": "10.0.0.1",
            "cpu_usage": 35.5,
            "memory_usage": 72.2,
            "status": "running",
        },
    )
    assert create_response.status_code == 201
    server_id = create_response.json()["id"]

    list_response = client.get("/api/v1/servers", headers=admin_headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    update_response = client.put(
        f"/api/v1/servers/{server_id}",
        headers=admin_headers,
        json={"cpu_usage": 49.1, "status": "degraded"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "degraded"

    delete_response = client.delete(f"/api/v1/servers/{server_id}", headers=admin_headers)
    assert delete_response.status_code == 204

    audit_response = client.get(
        "/api/v1/audit-logs",
        headers=admin_headers,
        params={"entity_type": "server"},
    )
    assert audit_response.status_code == 200
    actions = [item["action"] for item in audit_response.json()["items"]]
    assert "server.create" in actions
    assert "server.update" in actions
    assert "server.delete" in actions
