"""
This module contains simplified unit tests for the `AuthService` class. 
Which handles user authentication using FastAPI, JWT, and password hashing.

Tested Features:
- API root accessibility
- Token generation with valid and invalid credentials
- Protected route access with valid and invalid tokens

Dependencies:
- pytest
- fastapi
- fastapi.testclient
"""

import pytest
from fastapi.testclient import TestClient
from authservices import AuthService


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
        AccessTokenExpireMinutes=30,
    )
    return TestClient(service.App)


def test_root(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Authentication API is running."}


def test_token_generation(client):
    """Test token generation with valid credentials."""
    response = client.post(
        "/token",
        data={"username": "test", "password": "testpassword"},
    )
    assert response.status_code == 200
    assert "AccessToken" in response.json()


def test_invalid_token(client):
    """Test access with an invalid token."""
    response = client.get(
        "/users/me/", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401


def test_protected_route_with_token(client):
    """Test accessing a protected route with a valid token."""
    login_response = client.post(
        "/token",
        data={"username": "test", "password": "testpassword"},
    )
    token = login_response.json()["AccessToken"]
    response = client.get(
        "/users/me/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["Username"] == "test"
