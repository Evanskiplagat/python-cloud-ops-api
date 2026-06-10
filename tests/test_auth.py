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
    assert "refresh_token" in login_response.json()


def test_refresh_and_logout_revokes_tokens(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "devops@example.com",
            "full_name": "DevOps Engineer",
            "password": "password123",
            "role": "devops_engineer",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "devops@example.com", "password": "password123"},
    )
    tokens = login_response.json()

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    rotated_tokens = refresh_response.json()
    assert rotated_tokens["refresh_token"] != tokens["refresh_token"]

    reused_refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert reused_refresh_response.status_code == 401

    logout_response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {rotated_tokens['access_token']}"},
        json={"refresh_token": rotated_tokens["refresh_token"]},
    )
    assert logout_response.status_code == 204

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {rotated_tokens['access_token']}"},
    )
    assert me_response.status_code == 401
