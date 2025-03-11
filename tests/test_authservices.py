"""
This module contains unit tests for the `AuthService` class, which handles 
authentication using FastAPI, JWT, and password hashing with bcrypt.

Tested Features:
- Root endpoint accessibility
- Token generation with valid and invalid credentials
- Access to protected routes with valid and invalid tokens
- Authentication behavior for disabled users

These tests ensure that the authentication logic behaves as expected and 
provides accurate error handling and feedback.

Dependencies:
- pytest
- fastapi
- fastapi.testclient
"""

import pytest
from fastapi.testclient import TestClient
from authservices import AuthService
from fastapi import status

@pytest.fixture(scope="module")
def client():
    """
    Fixture to initialize the FastAPI TestClient for AuthService.

    Returns:
        TestClient: A test client for interacting with the AuthService API.
    """
    service = AuthService(
        Password="testpassword",
        Username="test",
        Email="test@example.com",
        FullName="Test User",
        Disabled=False,
        Algorithm="HS256",
        AccessTokenExpireMinutes=30
    )
    return TestClient(service.App)

def test_root(client):
    """
    Test to verify the root endpoint is accessible and responds correctly.

    Args:
        client (TestClient): The test client for API interaction.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Authentication API is running."}

def test_generate_token(client):
    """
    Test to verify the token generation endpoint with valid credentials.

    Args:
        client (TestClient): The test client for API interaction.
    """
    response = client.post(
        "/token",
        data={"username": "test", "password": "testpassword"},
    )
    assert response.status_code == 200
    assert "AccessToken" in response.json()
    assert "TokenType" in response.json()

def test_access_protected_route(client):
    """
    Test accessing a protected route with a valid token.

    Args:
        client (TestClient): The test client for API interaction.
    """
    login_response = client.post(
        "/token",
        data={"username": "test", "password": "testpassword"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["AccessToken"]
    
    response = client.get(
        "/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["Username"] == "test"

def test_invalid_token(client):
    """
    Test accessing a protected route with an invalid token.

    Args:
        client (TestClient): The test client for API interaction.
    """
    response = client.get(
        "/users/me/",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_incorrect_login(client):
    """
    Test login with incorrect credentials.

    Args:
        client (TestClient): The test client for API interaction.
    """
    response = client.post(
        "/token",
        data={"username": "wrong", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_disabled_user(client):
    """
    Test accessing a protected route with a disabled user account.

    Args:
        client (TestClient): The test client for API interaction.
    """
    service = AuthService(
        Password="disabledpass",
        Username="disabled",
        Email="disabled@example.com",
        FullName="Disabled User",
        Disabled=True,
        Algorithm="HS256",
        AccessTokenExpireMinutes=30
    )
    temp_client = TestClient(service.App)

    login_response = temp_client.post(
        "/token",
        data={"username": "disabled", "password": "disabledpass"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["AccessToken"]

    response = temp_client.get(
        "/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user"