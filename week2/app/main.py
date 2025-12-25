from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .db import init_db
from .routers import action_items, notes


class Settings(BaseModel):
    title: str = "Action Item Extractor"
    debug: bool = False
    database_path: Optional[str] = None


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    if settings is None:
        settings = Settings()
    
    app = FastAPI(title=settings.title, debug=settings.debug)
    
    # Initialize database on startup
    @app.on_event("startup")
    def startup_event():
        init_db()
    
    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
        return html_path.read_text(encoding="utf-8")

    app.include_router(notes.router)
    app.include_router(action_items.router)

    static_dir = Path(__file__).resolve().parents[1] / "frontend"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    return app


# Create the main app instance with default settings
app = create_app()