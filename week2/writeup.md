# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
```

Analyze the existing `extract_action_items()` function in `week2/app/services/extract.py`, which currently extracts action items using predefined heuristics.

Your task is to implement an **LLM-powered** alternative, `extract_action_items_llm()`, that utilizes Ollama to perform action item extraction via a large language model.

Some  tips:
- To produce structured outputs (i.e. JSON array of strings), refer to this documentation: https://ollama.com/blog/structured-outputs 
- To browse available Ollama models, refer to this documentation: https://ollama.com/library. Note that larger models will be more resource-intensive, so start small. To pull and run a model: `ollama run {MODEL_NAME}`

``` 

Generated Code Snippets:
```

def extract_action_items_llm(text: str) -> List[str]:
    """
    Extract action items from text using an LLM via Ollama.

    Args:
        text: Input text to extract action items from

    Returns:
        List of action items extracted from the text
    """
    # Define the prompt to extract action items
    prompt = f"""
You are an expert at extracting action items from text. Action items are specific tasks or to-dos that need to be completed.

Here is the input text:
{text}

Please extract all action items from the text and return them as a JSON array of strings. Each string should represent a single action item. If no action items are found, return an empty array. Action items typically include tasks that start with action verbs like 'create', 'implement', 'fix', 'update', 'write', 'check', 'verify', etc., or items marked with bullets, checkboxes [ ], or keywords like 'todo', 'action', 'next'.

Example outputs:
- ["Set up database", "Implement API endpoint", "Write tests"]
- ["Review documentation", "Update user interface"]
- []

Return ONLY the JSON array without any additional text or explanation.
"""

    # Use Ollama to generate the response with structured output
    response = chat(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),  # Use smaller model by default for efficiency
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0,  # Lower temperature for more consistent outputs
            "num_predict": 500,  # Limit response length
        },
        format="json",  # Request JSON format
    )

    # Extract the content from the response
    content = response['message']['content']

    # Parse the JSON response
    try:
        # The model should return a JSON array, so we parse it directly
        import json
        action_items = json.loads(content)

        # Ensure it's a list of strings
        if isinstance(action_items, list):
            return [str(item) for item in action_items if item]
        else:
            return []
    except json.JSONDecodeError:
        # If JSON parsing fails, return an empty list
        return []
    
```

### Exercise 2: Add Unit Tests
Prompt: 
```

Write unit tests for `extract_action_items_llm()` covering multiple inputs (e.g., bullet lists, keyword-prefixed lines, empty input) in `week2/tests/test_extract.py`.

``` 

Generated Code Snippets:
```

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

```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```

Perform a refactor of the code in the backend, focusing in particular on well-defined API contracts/schemas, database layer cleanup, app lifecycle/configuration, error handling. 

``` 

Generated/Modified Code Snippets:
```
skip
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```

1. Integrate the LLM-powered extraction as a new endpoint. Update the frontend to include an "Extract LLM" button that, when clicked, triggers the extraction process via the new endpoint.

2. Expose one final endpoint to retrieve all notes. Update the frontend to include a "List Notes" button that, when clicked, fetches and displays them.

``` 

Generated Code Snippets:
```
skip
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
analyze week2 codebase and generate a well-structured `README.md` file. The README should include, at a minimum:
- A brief overview of the project
- How to set up and run the project
- API endpoints and functionality
- Instructions for running the test suite

``` 

Generated Code Snippets:
```
skip
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 