"""
Build 2: Agent + REPLAgent
===========================
Agent = brain (loop, tools, sessions). REPLAgent = terminal UI.

Before running:
  mkdir -p notes

Tasks:
  1. Agent — chat(), run_once(), _run_loop(), dispatch(), _emit(), session I/O
  2. REPLAgent(Agent) — run() interactive loop
  3. resolve_path, read_file, write_file, list_files, edit_file
  4. main() — one-shot: python build2_agent_class.py "hello"

TUIAgent comes in the project (tui.py). No Textual imports here.
"""

"""
Build 2: Agent + REPLAgent
===========================
Agent = brain (loop, tools, sessions). REPLAgent = terminal UI.

Before running:
  mkdir -p notes
"""

import os
import sys
import json
import glob as glob_module
from openai import OpenAI
from dotenv import load_dotenv

# Import the memory system we built in Build 1
import build1_sessions as memory

load_dotenv()

# The Sandbox: The agent cannot access files outside this directory
WORKSPACE_ROOT = os.path.abspath(os.environ.get("WORKSPACE_ROOT", "."))
MAX_ITERATIONS = 10
MAX_READ_CHARS = 12_000

# Initialize the OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY", "dummy_key"),
)
# Use your preferred model
MODEL = "openrouter/free" 


# ==========================================
# 1. THE FILE TOOLS (Sandboxed)
# ==========================================

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
        
        # Prepend line numbers so the AI knows exactly what lines to target for edits
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
        # Default end_line to start_line if not provided (useful for single line replace/delete)
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
            # Append AFTER start_line
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
        # Make paths relative to workspace so the AI isn't confused by absolute paths
        rel_files = [os.path.relpath(f, WORKSPACE_ROOT) for f in files if os.path.isfile(f)]
        return {"content": "\n".join(rel_files) if rel_files else "No files found."}
    except Exception as e:
        return {"error": str(e)}


# ==========================================
# 2. TOOL SCHEMAS
# ==========================================

TOOLS = [
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


# ==========================================
# 3. THE AGENT CLASS HIERARCHY
# ==========================================

class Agent:
    """Core agent: brain, loop, tool dispatch. Zero UI logic here."""
    
    def __init__(self, workspace: str = ".", session_id: str | None = None):
        self.workspace = os.path.abspath(workspace)
        
        # Load an existing session, or create a brand new one
        if session_id:
            session_data = memory.load_session(session_id)
            self.session_id = session_data["id"]
            self.messages = session_data["messages"]
        else:
            self.session_id = memory.create_session()
            self.messages = [
                {"role": "system", "content": memory.build_system_prompt()}
            ]
            # Save the initial state immediately
            memory.save_session(self.session_id, self.messages, title="Untitled")

    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})
        memory.save_session(self.session_id, self.messages)  # Partial save
        return self._run_loop()

    def run_once(self, prompt: str) -> str:
        return self.chat(prompt)

    def _run_loop(self) -> str:
        for _ in range(MAX_ITERATIONS):
            response = client.chat.completions.create(
                model=MODEL,
                messages=self.messages,
                tools=TOOLS
            )
            
            message = response.choices[0].message
            
            # Convert the OpenAI object into a plain dictionary so JSON can save it!
            message_dict = message.model_dump(exclude_none=True)
            
            self.messages.append(message_dict)
            memory.save_session(self.session_id, self.messages)  # Partial save
            
            if not message.tool_calls:
                return message.content
                
            for tool_call in message.tool_calls:
                # Trigger the UI hook
                self._emit("tool_call", name=tool_call.function.name, args=tool_call.function.arguments)
                
                # Execute the tool
                tool_result = self.dispatch(tool_call)
                
                # Append the result
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })
                memory.save_session(self.session_id, self.messages)  # Partial save
                
        return "Hit max iterations."

    def dispatch(self, tool_call) -> dict:
        """Routes the LLM's JSON request to our actual Python functions."""
        name = tool_call.function.name
        try:
            args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON arguments"}
        
        if name == "write_file":
            return write_file(args.get("path"), args.get("content"))
        elif name == "read_file":
            return read_file(args.get("path"), args.get("start_line", 1), args.get("read_lines", 200))
        elif name == "edit_file":
            return edit_file(
                args.get("path"), 
                args.get("operation"), 
                args.get("start_line"), 
                args.get("end_line"), 
                args.get("content")
            )
        elif name == "list_files":
            return list_files(args.get("path", "."), args.get("pattern", "*"))
        
        return {"error": "Tool not recognized"}

    def _emit(self, event: str, **data) -> None:
        """A hook for subclasses (like the UI) to listen to what the brain is doing."""
        pass


class REPLAgent(Agent):
    """Terminal UI. Inherits the brain from Agent, adds print/input logic."""
    
    def run(self) -> None:
        print(f"Research Desk [Session: {self.session_id}] — Type /quit to exit")
        while True:
            try:
                user_input = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not user_input or user_input in ("/quit", "/exit"):
                break
            print("\nAgent:", self.chat(user_input))

    def _emit(self, event: str, **data) -> None:
        if event == "tool_call":
            print(f"  [⚡ Executing Tool] {data.get('name')}", file=sys.stderr)


# ==========================================
# 4. ENTRY POINT
# ==========================================

def main():
    # Make sure notes directory exists before the agent tries to write to it
    os.makedirs("notes", exist_ok=True)
    
    agent = REPLAgent()
    
    # One-shot CLI mode if the user passes a prompt in the terminal command
    if len(sys.argv) > 1:
        print(agent.run_once(" ".join(sys.argv[1:])))
        return
        
    # Otherwise, start the interactive loop
    agent.run()

if __name__ == "__main__":
    main()