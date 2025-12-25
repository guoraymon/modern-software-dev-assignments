from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters

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
    print("prompt", prompt)
    response = chat(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),  # Use smaller model by default for efficiency
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0,  # Lower temperature for more consistent outputs
            "num_predict": 500,  # Limit response length
        },
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
    