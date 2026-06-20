"""
Build 1: Session Store
========================
Save and resume conversations on disk. Load AGENTS.md into the system prompt.

Tasks:
  1. create_session() -> session_id
  2. save_session(session_id, messages, title?)
  3. load_session(session_id) -> {id, title, messages, ...}
  4. list_sessions() -> [{id, title, updated_at}, ...]
  5. build_system_prompt() -> base + AGENTS.md contents

Run twice: save a session in run 1, load it in run 2 and confirm messages restored.
"""

"""
Build 1: Session Store
========================
Save and resume conversations on disk. Load AGENTS.md into the system prompt.
"""

import json
import os
import uuid
from datetime import datetime, timezone
import glob

SESSIONS_DIR = ".agent/sessions"
AGENTS_PATHS = ("AGENTS.md", ".agent/AGENTS.md")

BASE_PROMPT = "You are Research Desk, a helpful research assistant."

def create_session() -> str:
    """Return a new 8-char hex session ID."""
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    # Generate a random UUID and take the first 8 characters
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
    
    # Write the data to a JSON file safely
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
    """Return sessions sorted by updated_at descending."""
    if not os.path.exists(SESSIONS_DIR):
        return []
        
    sessions = []
    # Glob finds all .json files in the directory
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
            continue # Skip corrupted files
            
    # Sort by the ISO timestamp, newest first
    return sorted(sessions, key=lambda x: x["updated_at"], reverse=True)

def build_system_prompt() -> str:
    """Base prompt + AGENTS.md if it exists."""
    parts = [BASE_PROMPT]
    
    for path in AGENTS_PATHS:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                parts.append(f"## Project rules\n{f.read()}")
            break # Stop looking once we find one
            
    return "\n\n".join(parts)

if __name__ == "__main__":
    # Test the implementation
    sid = create_session()
    messages = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": "What is a surface code?"},
        {"role": "assistant", "content": "A surface code is a type of quantum error correcting code."},
    ]
    
    save_session(sid, messages, title="Quantum error correction")
    print(f"Saved session: {sid}")
    
    sessions = list_sessions()
    print(f"All sessions: {sessions}")
    
    loaded_data = load_session(sid)
    print(f"Loaded title: {loaded_data['title']}")