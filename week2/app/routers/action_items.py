from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException

from .. import db
from ..models import (
    ActionItem,
    ActionItemMarkDoneRequest,
    ExtractActionItemsRequest,
    ExtractActionItemsResponse
)
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractActionItemsResponse)
def extract(payload: ExtractActionItemsRequest) -> ExtractActionItemsResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id: Optional[int] = None
    if payload.save_note:
        try:
            note_id = db.insert_note(text)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    items = extract_action_items(text)
    try:
        ids = db.insert_action_items(items, note_id=note_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    action_items = [
        ActionItem(
            id=i,
            text=t,
            note_id=note_id,
            done=False,
            created_at=None  # Will be filled by database
        ) for i, t in zip(ids, items)
    ]

    return ExtractActionItemsResponse(note_id=note_id, items=action_items)


@router.post("/extract-llm", response_model=ExtractActionItemsResponse)
def extract_llm(payload: ExtractActionItemsRequest) -> ExtractActionItemsResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id: Optional[int] = None
    if payload.save_note:
        try:
            note_id = db.insert_note(text)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    items = extract_action_items_llm(text)
    try:
        ids = db.insert_action_items(items, note_id=note_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    action_items = [
        ActionItem(
            id=i,
            text=t,
            note_id=note_id,
            done=False,
            created_at=None  # Will be filled by database
        ) for i, t in zip(ids, items)
    ]

    return ExtractActionItemsResponse(note_id=note_id, items=action_items)


@router.get("", response_model=List[ActionItem])
def list_all(note_id: Optional[int] = None) -> List[ActionItem]:
    try:
        rows = db.list_action_items(note_id=note_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return [
        ActionItem(
            id=r.id,
            note_id=r.note_id,
            text=r.text,
            done=bool(r.done),
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done")
def mark_done(action_item_id: int, request: ActionItemMarkDoneRequest) -> dict:
    try:
        db.mark_action_item_done(action_item_id, request.done)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": action_item_id, "done": request.done}


