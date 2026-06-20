import os
import json
import uuid
from datetime import datetime, timezone
import glob

SESSIONS_DIR = ".agent/sessions"
AGENTS_PATHS = ("AGENTS.md", ".agent/AGENTS.md")

BASE_PROMPT = "You are Research Desk, a helpful research assistant."

def create_session() -> str:
    """Return a new 8-char hex session ID."""
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    return uuid.uuid4().hex[:8]

def save_session(session_id: str, messages: list, title: str = "Untitled") -> None:
    """Write session JSON to .agent/sessions/{id}.json"""
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    
    session_data = {
        "id": session_id,
        "title": title,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "messages": messages
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2)

def load_session(session_id: str) -> dict:
    """Load and return session dict including messages list."""
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Session file not found: {filepath}")
        
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def list_sessions() -> list[dict]:
    """Return sessions sorted by updated_at descending (newest first)."""
    if not os.path.exists(SESSIONS_DIR):
        return []
        
    sessions = []
    for filepath in glob.glob(os.path.join(SESSIONS_DIR, "*.json")):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                sessions.append({
                    "id": data.get("id"),
                    "title": data.get("title", "Untitled"),
                    "updated_at": data.get("updated_at")
                })
        except Exception:
            continue
            
    return sorted(sessions, key=lambda x: x["updated_at"], reverse=True)

def build_system_prompt() -> str:
    """Base prompt + AGENTS.md if it exists."""
    parts = [BASE_PROMPT]
    
    for path in AGENTS_PATHS:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                parts.append(f"## Project rules\n{f.read()}")
            break
            
    return "\n\n".join(parts)