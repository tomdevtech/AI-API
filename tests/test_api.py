"""
This module contains unit tests for the `ApiManager` class, which manages
AI model interactions including creation, chat, and API key validation using FastAPI and Ollama.

Tested Features:
- Root endpoint accessibility
- Token generation and API key handling
- AI model generation, chat, and basic operations like create, show, delete, etc.
- Error handling for invalid API keys and insufficient credits

These tests ensure the API behaves as expected for authorized and unauthorized access.

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
    """
    Test to verify the root endpoint is accessible and responds correctly.

    Args:
        client (TestClient): The test client for API interaction.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_generate_key(client):
    """
    Test to generate a new API key when no credits are left.

    Args:
        client (TestClient): The test client for API interaction.
    """
    response = client.post("/generate-key")
    if response.status_code == 401:
        assert response.json()["detail"] == "API Key creation not necessary."
    else:
        assert response.status_code == 200
        assert "api_key" in response.json()


def test_generate_model_response(client):
    """
    Test to generate a response from the AI model.

    Args:
        client (TestClient): The test client for API interaction.
    """
    api_key = client.get("/").json().get("initial_api_key")
    headers = {"XApiKey": api_key}
    response = client.post(
        "/generate", params={"Prompt": "Hello", "Model": "test_model"}, headers=headers
    )
    assert response.status_code == 200


def test_chat_with_model(client):
    """
    Test to initiate a chat with the AI model.

    Args:
        client (TestClient): The test client for API interaction.
    """
    api_key = client.get("/").json().get("initial_api_key")
    headers = {"XApiKey": api_key}
    response = client.post(
        "/chat", params={"Prompt": "Hello", "Model": "test_model"}, headers=headers
    )
    assert response.status_code == 200


def test_list_model_tags(client):
    """
    Test to list all available AI model tags.

    Args:
        client (TestClient): The test client for API interaction.
    """
    api_key = client.get("/").json().get("initial_api_key")
    headers = {"XApiKey": api_key}
    response = client.get("/tags", headers=headers)
    assert response.status_code == 200


def test_create_model(client):
    """
    Test to create a new AI model.

    Args:
        client (TestClient): The test client for API interaction.
    """
    api_key = client.get("/").json().get("initial_api_key")
    headers = {"XApiKey": api_key}
    response = client.post("/create", params={"Model": "new_model"}, headers=headers)
    assert response.status_code == 200


def test_show_model(client):
    """
    Test to show details of a specific AI model.

    Args:
        client (TestClient): The test client for API interaction.
    """
    api_key = client.get("/").json().get("initial_api_key")
    headers = {"XApiKey": api_key}
    response = client.post("/show", params={"Model": "test_model"}, headers=headers)
    assert response.status_code == 200


def test_delete_model(client):
    """
    Test to delete an AI model.

    Args:
        client (TestClient): The test client for API interaction.
    """
    api_key = client.get("/").json().get("initial_api_key")
    headers = {"XApiKey": api_key}
    response = client.delete("/delete", params={"Model": "test_model"}, headers=headers)
    assert response.status_code == 200


def test_invalid_api_key(client):
    """
    Test accessing endpoints with an invalid API key.

    Args:
        client (TestClient): The test client for API interaction.
    """
    response = client.post(
        "/generate",
        params={"Prompt": "Hello", "Model": "test_model"},
        headers={"XApiKey": "invalid_key"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "API Key not found."


def test_no_credits_left(client):
    """
    Test behavior when an API key runs out of credits.

    Args:
        client (TestClient): The test client for API interaction.
    """
    api_key = client.get("/").json().get("initial_api_key")
    headers = {"XApiKey": api_key}
    for _ in range(6):
        client.post(
            "/generate",
            params={"Prompt": "Hello", "Model": "test_model"},
            headers=headers,
        )
    response = client.post(
        "/generate", params={"Prompt": "Hello", "Model": "test_model"}, headers=headers
    )
    assert response.status_code == 401
    assert (
        response.json()["detail"] == "No credits left. Please generate a new API key."
    )


def test_version(client):
    """
    Test to check the version of Ollama.

    Args:
        client (TestClient): The test client for API interaction.
    """
    api_key = client.get("/").json().get("initial_api_key")
    headers = {"XApiKey": api_key}
    response = client.post("/version", headers=headers)
    assert response.status_code == 200
    assert "version" in response.json()
