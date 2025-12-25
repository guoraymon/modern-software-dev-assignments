# Action Item Extractor

This is a FastAPI-based web application that converts free-form notes into enumerated action items. The application provides both traditional rule-based extraction and LLM-powered extraction capabilities.

## Overview

The Action Item Extractor is designed to parse notes and extract actionable items using two approaches:
1. **Traditional extraction**: Uses predefined heuristics to identify action items
2. **LLM-powered extraction**: Leverages Ollama to extract action items using large language models

The application includes a minimal HTML frontend for user interaction and a SQLite database for persistence.

## Features

- Extract action items from text using both traditional and LLM methods
- Save notes to the database
- Mark action items as done/undone
- List all notes and action items
- Clean, responsive HTML interface

## Prerequisites

- Python 3.8+
- Ollama (for LLM-powered extraction)
- A supported Ollama model (e.g., llama3.2)

## Setup and Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies using Poetry
   poetry install
   ```

3. **Set up Ollama**
   ```bash
   # Install Ollama from https://ollama.ai
   # Pull a model (e.g., llama3.2)
   ollama pull llama3.2
   ```

4. **Configure environment variables (optional)**
   Create a `.env` file in the project root:
   ```env
   OLLAMA_MODEL=llama3.2
   ```

## Running the Application

1. **Start Ollama server**
   ```bash
   ollama serve
   ```

2. **Run the application**
   ```bash
   poetry run uvicorn week2.app.main:app --reload
   ```

3. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000/`

## API Endpoints

### Notes Endpoints
- `POST /notes` - Create a new note
  - Request body: `{"content": "note content"}`
  - Response: `{"id": 1, "content": "note content", "created_at": "timestamp"}`

- `GET /notes` - List all notes
  - Response: Array of note objects

- `GET /notes/{note_id}` - Get a specific note
  - Response: Note object

### Action Items Endpoints
- `POST /action-items/extract` - Extract action items using traditional method
  - Request body: `{"text": "notes text", "save_note": true/false}`
  - Response: `{"note_id": 1, "items": [...]}`

- `POST /action-items/extract-llm` - Extract action items using LLM
  - Request body: `{"text": "notes text", "save_note": true/false}`
  - Response: `{"note_id": 1, "items": [...]}`

- `GET /action-items` - List all action items (with optional note_id filter)
  - Query parameters: `note_id` (optional)
  - Response: Array of action item objects

- `POST /action-items/{action_item_id}/done` - Mark an action item as done
  - Request body: `{"done": true/false}`
  - Response: `{"id": 1, "done": true}`

## Frontend Functionality

The frontend provides a simple interface with the following features:

- **Text area** for entering notes
- **Save as note** checkbox to save notes to the database
- **Extract** button for traditional action item extraction
- **Extract LLM** button for LLM-powered action item extraction
- **List Notes** button to view all saved notes
- **Checkboxes** to mark action items as done/undone

## Running Tests

The project includes comprehensive unit tests for both the extraction logic and API endpoints.

### Run all tests
```bash
poetry run pytest week2/tests/ -v
```

### Run specific test files
```bash
# Run extraction tests
poetry run pytest week2/tests/test_extract.py -v

# Run API tests
poetry run pytest week2/tests/test_api.py -v
```

### Test Coverage
- Traditional extraction functionality
- LLM-powered extraction (with mocking)
- API endpoints with proper request/response validation
- Error handling scenarios
- Database operations

## Project Structure

```
week2/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── db.py                # Database operations
│   ├── models.py            # Pydantic models for API contracts
│   ├── db_models.py         # Dataclasses for database records
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── action_items.py  # Action items API routes
│   │   └── notes.py         # Notes API routes
│   └── services/
│       └── extract.py       # Extraction logic
├── tests/
│   ├── __init__.py
│   ├── test_extract.py      # Extraction logic tests
│   └── test_api.py          # API endpoint tests
├── frontend/
│   └── index.html           # Frontend interface
├── data/                    # SQLite database directory (auto-created)
├── README.md
└── assignment.md
```

## Configuration

The application uses the following configuration:

- **Database**: SQLite file stored in the `data/` directory
- **Model**: Configurable via `OLLAMA_MODEL` environment variable (defaults to `llama3.2`)
- **Server**: FastAPI with automatic database initialization on startup

## Troubleshooting

1. **Ollama not responding**: Ensure Ollama server is running with `ollama serve`
2. **Model not found**: Download the required model with `ollama pull <model-name>`
3. **Database errors**: The application will automatically create the database and tables on first run
4. **Frontend not loading**: Ensure the server is running and check browser console for errors

## Technologies Used

- **Backend**: FastAPI, Pydantic, SQLite
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **LLM Integration**: Ollama Python client
- **Testing**: pytest, TestClient
- **Dependency Management**: Poetry