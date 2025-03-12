"""
This module contains simplified unit tests for the `ApiManager` class.
Which handles AI model management, including API key handling and model interactions using FastAPI.

Tested Features:
- API root accessibility
- API key generation
- Model interaction endpoints like `generate`, `create`, and `delete`

Dependencies:
- pytest
- fastapi
- fastapi.testclient
"""

import pytest
from fastapi.testclient import TestClient
from api import ApiManager


@pytest.fixture(scope="module")
def client():
    """
    Fixture to initialize the FastAPI TestClient for ApiManager.

    Returns:
        TestClient: A test client for interacting with the ApiManager API.
    """
    manager = ApiManager()
    return TestClient(manager.App)


def test_root(client):
    """Test the root endpoint to ensure the API is running."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_generate_api_key(client):
    """Test the generation of a new API key."""
    response = client.post("/generate-key")
    if response.status_code == 401:
        assert response.json()["detail"] == "API Key creation not necessary."
    else:
        assert response.status_code == 200
        assert "api_key" in response.json()


def test_generate_with_valid_api_key(client):
    """Test the 'generate' endpoint with a valid API key."""
    api_key = client.get("/").json().get("initial_api_key")
    headers = {"XApiKey": api_key}
    response = client.post("/generate", params={"Prompt": "Hello", "Model": "test-model"}, headers=headers)
    assert response.status_code == 200


def test_generate_with_invalid_api_key(client):
    """Test the 'generate' endpoint with an invalid API key."""
    response = client.post("/generate", params={"Prompt": "Hello", "Model": "test-model"}, headers={"XApiKey": "invalid"})
    assert response.status_code == 401
    assert response.json()["detail"] == "API Key not found."


def test_create_model(client):
    """Test the creation of a new model."""
    api_key = client.get("/").json().get("initial_api_key")
    headers = {"XApiKey": api_key}
    response = client.post("/create", params={"Model": "test-model"}, headers=headers)
    assert response.status_code == 200


def test_delete_model(client):
    """Test the deletion of a model."""
    api_key = client.get("/").json().get("initial_api_key")
    headers = {"XApiKey": api_key}
    response = client.delete("/delete", params={"Model": "test-model"}, headers=headers)
    assert response.status_code == 200
