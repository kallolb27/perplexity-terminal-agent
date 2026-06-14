"""
Build 1: Custom Tool Call Parser
=================================
Before modern SDKs handled tool calls natively, developers used custom text formats
that the model was prompted to emit. This build has you implement that pattern from
scratch: prompt the model to emit tool calls in a structured format, parse them, run
the corresponding Python function, and feed the result back.

This is NOT the production way to do it (Build 2 is). But doing it manually first
makes the mechanics obvious. The SDK is doing exactly this, just more robustly.

The format we'll use:
    The model emits tool calls wrapped in <tool_call> tags, like:

        I need to read the file first.

        <tool_call>
        {"name": "read_file", "arguments": {"path": "notes.txt"}}
        </tool_call>

    Your code finds the tag, parses the JSON, runs the function, and injects
    the result back as a <tool_response> in the next message.

Tasks:
  1. Complete `parse_tool_call` to extract name + arguments from a model response
  2. Complete `dispatch` to route a tool call to the right Python function
  3. Complete `run_agent` to implement the back-and-forth loop

Tools to implement:
  - read_file(path: str) -> dict    reads a file from disk and returns its content
  - write_file(path: str, content: str) -> dict    writes content to a file on disk

Before running, create a file called `sample.txt` with some text in it.
"""

import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

MODEL = "openrouter/free"

SYSTEM_PROMPT = """You are a helpful file assistant with access to the following tools:

- read_file(path: str): reads a file from disk and returns its content
- write_file(path: str, content: str): writes content to a file on disk

When you need to use a tool, emit EXACTLY this format and nothing else after it:

<tool_call>
{"name": "TOOL_NAME", "arguments": {"arg1": "value1"}}
</tool_call>

After you receive the tool result in a <tool_response> block, continue your response
normally. Do not emit a tool_call and prose in the same turn. Pick one or the other.
"""

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def read_file(path: str) -> dict:
    """
    Read a file from disk and return its content.
    Return {"content": ..., "path": ...} on success.
    Return {"error": ...} if the file doesn't exist or can't be read.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content, "path": path}
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}


def write_file(path: str, content: str) -> dict:
    """
    Write content to a file on disk.
    Return {"success": True, "path": ..., "bytes_written": ...} on success.
    Return {"error": ...} on failure.
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            bytes_written = f.write(content)
        return {"success": True, "path": path, "bytes_written": bytes_written}
    except Exception as e:
        return {"error": f"Failed to write file: {str(e)}"}

# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_tool_call(response_text: str) -> dict | None:
    """
    Extract a tool call from the model's response text.
    """
    # re.DOTALL makes the '.' match newlines too, so we capture the whole block
    match = re.search(r"<tool_call>(.*?)</tool_call>", response_text, flags=re.DOTALL)
    
    if match:
        try:
            # Group 1 is the text *inside* the tags. We parse it as JSON.
            json_str = match.group(1).strip()
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("[Error: AI generated invalid JSON inside the tool call]")
            return None
            
    return None


def strip_tool_call(response_text: str) -> str:
    """
    Return the response text with any <tool_call>...</tool_call> block removed.
    """
    # Simply replace the entire tag block with an empty string
    return re.sub(r"<tool_call>.*?</tool_call>", "", response_text, flags=re.DOTALL).strip()


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

TOOL_REGISTRY = {
    "read_file": read_file,
    "write_file": write_file,
}

def dispatch(name: str, arguments: dict) -> str:
    """
    Look up the tool by name, call it with the given arguments, and return a
    JSON string of the result.
    """
    # 1. Check if the tool exists in our registry
    if name not in TOOL_REGISTRY:
        return json.dumps({"error": f"Unknown tool: {name}"})
        
    tool_fn = TOOL_REGISTRY[name]
    
    # 2. Try running the function with the arguments the AI provided
    try:
        # **arguments unpacks the dictionary into function arguments
        result = tool_fn(**arguments)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

MAX_ITERATIONS = 6

def run_agent(user_message: str) -> str:
    """Run the tool-calling agent loop for a single user message."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    for iteration in range(MAX_ITERATIONS):
        # 1. Call the model
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
        assistant_text = response.choices[0].message.content
        
        # We must append the AI's exact reply to the history so it remembers
        messages.append({"role": "assistant", "content": assistant_text})
        
        # 2. Check if the AI output a <tool_call> tag
        tool_call = parse_tool_call(assistant_text)
        
        if tool_call:
            # Print to terminal so we can watch it work
            print(f"   [System: AI requested tool '{tool_call['name']}']")
            
            # 3. Run the tool using our dispatcher
            result_json = dispatch(tool_call["name"], tool_call.get("arguments", {}))
            
            # 4. Inject the result back as a <tool_response>
            tool_feedback = f"<tool_response>\n{result_json}\n</tool_response>"
            messages.append({"role": "user", "content": tool_feedback})
            
            # The loop goes back to the top to let the AI think again!
        else:
            # 5. If no tool was called, the AI is done. Return the final answer!
            return strip_tool_call(assistant_text)

    return f"[Agent stopped after {MAX_ITERATIONS} iterations]"
# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Create a sample file for the agent to work with
    with open("sample.txt", "w", encoding="utf-8") as f:
        f.write("IIT Delhi was established in 1961. It is one of the premier engineering institutions in India.\n")
        f.write("The campus spans 325 acres in Hauz Khas, New Delhi.\n")

    test_queries = [
        "Read sample.txt and summarise what it says.",
        "Read sample.txt and write a one-sentence version of its content to summary.txt.",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        result = run_agent(query)
        print(f"Answer: {result}")