import os
import pytest
from unittest.mock import patch, MagicMock

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


@patch('week2.app.services.extract.chat')
def test_extract_action_items_llm_bullets_and_checkboxes(mock_chat):
    # Mock the Ollama chat response
    mock_response = {
        'message': {
            'content': '["Set up database", "Implement API extract endpoint", "Write tests"]'
        }
    }
    mock_chat.return_value = mock_response

    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items_llm(text)
    # The LLM should identify action items with checkboxes and bullet points
    assert isinstance(items, list)
    assert "Set up database" in items
    assert "Implement API extract endpoint" in items
    assert "Write tests" in items


@patch('week2.app.services.extract.chat')
def test_extract_action_items_llm_keyword_prefixed(mock_chat):
    # Mock the Ollama chat response
    mock_response = {
        'message': {
            'content': '["Complete assignment", "Review code changes", "Deploy to production"]'
        }
    }
    mock_chat.return_value = mock_response

    text = """
    Daily tasks:
    todo: Complete assignment
    action: Review code changes
    next: Deploy to production
    Regular sentence without action.
    """.strip()

    items = extract_action_items_llm(text)
    assert isinstance(items, list)
    # The LLM should identify action items prefixed with keywords
    assert "Complete assignment" in items
    assert "Review code changes" in items
    assert "Deploy to production" in items


@patch('week2.app.services.extract.chat')
def test_extract_action_items_llm_empty_input(mock_chat):
    # Mock the Ollama chat response for empty input
    mock_response = {
        'message': {
            'content': '[]'
        }
    }
    mock_chat.return_value = mock_response

    text = ""

    items = extract_action_items_llm(text)
    assert isinstance(items, list)
    assert len(items) == 0


@patch('week2.app.services.extract.chat')
def test_extract_action_items_llm_no_action_items(mock_chat):
    # Mock the Ollama chat response for text without action items
    mock_response = {
        'message': {
            'content': '[]'
        }
    }
    mock_chat.return_value = mock_response

    text = """
    This is just a narrative text.
    It contains no actionable items.
    Just regular sentences describing things.
    """.strip()

    items = extract_action_items_llm(text)
    assert isinstance(items, list)
    assert len(items) == 0


@patch('week2.app.services.extract.chat')
def test_extract_action_items_llm_malformed_response(mock_chat):
    # Test when the LLM returns malformed JSON
    mock_response = {
        'message': {
            'content': 'This is not JSON'
        }
    }
    mock_chat.return_value = mock_response

    text = "Some text"

    items = extract_action_items_llm(text)
    # Should return empty list when JSON parsing fails
    assert isinstance(items, list)
    assert len(items) == 0


@patch('week2.app.services.extract.chat')
def test_extract_action_items_llm_various_formats(mock_chat):
    # Test with various text formats including mixed content
    mock_response = {
        'message': {
            'content': '["Fix bug in login module", "Update documentation for API", "Schedule team meeting"]'
        }
    }
    mock_chat.return_value = mock_response

    text = """
    Meeting notes:
    [ ] Fix bug in login module
    Action: Update documentation for API
    Next steps: Schedule team meeting
    Random comment that is not an action item.
    - Implement new feature
    todo: Review pull requests
    """.strip()

    items = extract_action_items_llm(text)
    assert isinstance(items, list)
    assert len(items) >= 3  # Should have at least the 3 main action items
    assert any("Fix bug" in item for item in items)
    assert any("Update documentation" in item for item in items)
    assert any("Schedule team meeting" in item for item in items)
