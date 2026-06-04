def test_register_and_login(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "devops@example.com",
            "full_name": "DevOps Engineer",
            "password": "password123",
            "role": "devops_engineer",
        },
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "devops@example.com"

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "devops@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
