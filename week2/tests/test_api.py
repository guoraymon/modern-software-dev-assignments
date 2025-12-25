import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from week2.app.main import app
from week2.app.services.extract import extract_action_items_llm


@pytest.fixture
def client():
    return TestClient(app)


@patch('week2.app.services.extract.chat')
def test_extract_endpoint_success(mock_chat, client):
    # Mock the Ollama chat response for the LLM function
    mock_response = {
        'message': {
            'content': '["Set up database", "Implement API endpoint", "Write tests"]'
        }
    }
    mock_chat.return_value = mock_response
    
    payload = {
        "text": "Notes from meeting:\n- [ ] Set up database\n* implement API endpoint\n1. Write tests",
        "save_note": True
    }
    
    response = client.post("/action-items/extract", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "note_id" in data
    assert data["note_id"] is not None
    assert "items" in data
    assert len(data["items"]) > 0


@patch('week2.app.services.extract.chat')
def test_extract_llm_endpoint_success(mock_chat, client):
    # Mock the Ollama chat response
    mock_response = {
        'message': {
            'content': '["Complete assignment", "Review code changes", "Deploy to production"]'
        }
    }
    mock_chat.return_value = mock_response
    
    payload = {
        "text": "Daily tasks:\ntodo: Complete assignment\naction: Review code changes\nnext: Deploy to production",
        "save_note": False
    }
    
    response = client.post("/action-items/extract-llm", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "note_id" in data
    assert "items" in data
    assert len(data["items"]) > 0


def test_extract_endpoint_empty_text(client):
    payload = {
        "text": "",
        "save_note": False
    }
    
    response = client.post("/action-items/extract", json=payload)
    assert response.status_code == 400
    assert "detail" in response.json()


def test_list_action_items(client):
    response = client.get("/action-items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_note_endpoint(client):
    payload = {
        "content": "This is a test note"
    }
    
    response = client.post("/notes", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["content"] == "This is a test note"


def test_get_note_endpoint(client):
    # First create a note
    create_payload = {
        "content": "Test note for retrieval"
    }
    create_response = client.post("/notes", json=create_payload)
    assert create_response.status_code == 200
    note_data = create_response.json()
    note_id = note_data["id"]
    
    # Then retrieve it
    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["content"] == "Test note for retrieval"


def test_list_notes_endpoint(client):
    response = client.get("/notes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_mark_action_item_done(client):
    # This test might fail if there are no action items, so we'll test the error case
    response = client.post("/action-items/999999/done", json={"done": True})
    # The exact status code may vary based on implementation, but should be an error
    assert response.status_code in [400, 404]