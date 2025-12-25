from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class NoteRecord:
    id: int
    content: str
    created_at: str


@dataclass
class ActionItemRecord:
    id: int
    note_id: Optional[int]
    text: str
    done: int  # 0 or 1
    created_at: str