"""
Sandboxed file tools — see week_3/2_agent_class.md

Implement:
  - resolve_path
  - read_file(path, start_line=1, read_lines=200)  — numbered lines, has_more
  - write_file(path, content)
  - edit_file(path, operation, start_line, end_line?, content?)  — replace | delete | append
  - list_files(path, pattern)
"""

# TODO: implement — see Build 2
import os
import glob as glob_module

# The Sandbox boundary
WORKSPACE_ROOT = os.path.abspath(os.environ.get("WORKSPACE_ROOT", "."))
MAX_READ_CHARS = 12_000

def resolve_path(path: str) -> str:
    """Ensure the requested path is safely within the workspace sandbox."""
    full_path = os.path.abspath(os.path.join(WORKSPACE_ROOT, path))
    if not full_path.startswith(WORKSPACE_ROOT):
        raise ValueError(f"Security Error: Path '{path}' escapes the workspace sandbox.")
    return full_path

def read_file(path: str, start_line: int = 1, read_lines: int = 200) -> dict:
    """Read a specific window of lines from a file, returning numbered lines."""
    try:
        full_path = resolve_path(path)
        if not os.path.exists(full_path):
            return {"error": f"File not found: {path}"}

        with open(full_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        total_lines = len(lines)
        start_idx = max(0, start_line - 1)
        end_idx = min(start_idx + read_lines, total_lines)
        
        snippet = lines[start_idx:end_idx]
        
        numbered_snippet = [f"{i + start_line}| {line}" for i, line in enumerate(snippet)]
        content = "\n".join(numbered_snippet)

        if len(content) > MAX_READ_CHARS:
            content = content[:MAX_READ_CHARS] + "\n...[truncated]"

        return {
            "content": content,
            "total_lines": total_lines,
            "has_more": end_idx < total_lines
        }
    except Exception as e:
        return {"error": str(e)}

def write_file(path: str, content: str) -> dict:
    """Create a new file or overwrite an existing one."""
    try:
        full_path = resolve_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"content": f"Successfully wrote to {path}"}
    except Exception as e:
        return {"error": str(e)}

def edit_file(path: str, operation: str, start_line: int, end_line: int | None = None, content: str | None = None) -> dict:
    """Surgically edit specific lines inside a file without overwriting the whole thing."""
    try:
        full_path = resolve_path(path)
        if not os.path.exists(full_path):
            return {"error": f"File not found: {path}"}
            
        with open(full_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            
        start_idx = max(0, start_line - 1)
        end_idx = max(0, end_line - 1) if end_line else start_idx
        
        if operation == "replace":
            new_lines = content.splitlines() if content else []
            lines[start_idx:end_idx + 1] = new_lines
            preview = f"Replaced lines {start_line}-{end_line}."
        elif operation == "delete":
            del lines[start_idx:end_idx + 1]
            preview = f"Deleted lines {start_line}-{end_line}."
        elif operation == "append":
            new_lines = content.splitlines() if content else []
            lines = lines[:start_idx + 1] + new_lines + lines[start_idx + 1:]
            preview = f"Appended {len(new_lines)} lines after line {start_line}."
        else:
            return {"error": f"Unknown operation: {operation}"}
            
        with open(full_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
            
        return {"content": f"Success. {preview}"}
    except Exception as e:
        return {"error": str(e)}

def list_files(path: str = ".", pattern: str = "*") -> dict:
    """List files in the workspace so the AI can navigate."""
    try:
        full_path = resolve_path(path)
        search_pattern = os.path.join(full_path, "**", pattern)
        files = glob_module.glob(search_pattern, recursive=True)
        rel_files = [os.path.relpath(f, WORKSPACE_ROOT) for f in files if os.path.isfile(f)]
        return {"content": "\n".join(rel_files) if rel_files else "No files found."}
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# TOOL SCHEMAS FOR THE AGENT
# ==========================================

FILE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write new content to a file. Used for creating new notes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path, e.g., notes/topic.md"},
                    "content": {"type": "string", "description": "The markdown content to write"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read lines from a file. Returns numbered lines for accurate editing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "start_line": {"type": "integer", "description": "Line to start reading from (1-indexed)"},
                    "read_lines": {"type": "integer", "description": "Number of lines to read"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit specific lines in a file. Always read_file first to check line numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "operation": {"type": "string", "enum": ["replace", "delete", "append"]},
                    "start_line": {"type": "integer"},
                    "end_line": {"type": "integer"},
                    "content": {"type": "string", "description": "New content for replace/append"}
                },
                "required": ["path", "operation", "start_line"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory to see what notes already exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory to search (default '.')"},
                    "pattern": {"type": "string", "description": "Glob pattern (default '*')"}
                },
                "required": []
            }
        }
    }
]