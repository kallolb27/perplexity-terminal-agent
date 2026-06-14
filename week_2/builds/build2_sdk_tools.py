"""
Build 2: Tool Calling with the OpenAI SDK
==========================================
Build 1 had you implement the tool-call round-trip by hand using a custom text format.
This build does the same thing the production way: using the OpenAI SDK's native
`tools` parameter, `tool_calls` response field, and `"role": "tool"` messages.

The mechanics are identical. You're still parsing a tool name, running a function,
and sending the result back. The difference is that the SDK handles the encoding
and the model is trained to produce structured JSON tool calls rather than freeform XML.

Implement the same two tools as Build 1:
  - get_weather(city: str) -> dict
  - calculate(expression: str) -> dict

Then complete the agent loop and watch the pattern become clean.

Stretch goals (not required):
  - Add a third tool: get_time(timezone: str) -> dict
  - Handle multiple tool_calls in a single response (the model can call several at once)
  - Add a token counter that prints total tokens used after the loop ends
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

# Using our trusty free auto-router!
MODEL = "openrouter/free"

# ---------------------------------------------------------------------------
# 1. Tool Implementations
# ---------------------------------------------------------------------------

def get_weather(city: str, unit: str = "celsius") -> dict:
    """Mock weather API."""
    print(f"   [Executing get_weather for {city} in {unit}...]")
    # In a real app, this would call a real weather API
    return {"city": city, "temperature": 22, "unit": unit, "forecast": "Sunny with a light breeze"}

def calculate(expression: str) -> dict:
    """Simple calculator."""
    print(f"   [Executing calculate for '{expression}'...]")
    try:
        # NOTE: eval() is dangerous in production, but fine for our local test script!
        result = eval(expression)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

# ---------------------------------------------------------------------------
# 2. The Official JSON Schema (The "Menu" we send to the AI)
# ---------------------------------------------------------------------------

my_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "The name of the city, e.g., 'Paris'"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "The math expression, e.g., '24 * 7'"}
                },
                "required": ["expression"]
            }
        }
    }
]

# ---------------------------------------------------------------------------
# 3. The Dispatcher
# ---------------------------------------------------------------------------

def dispatch(tool_call) -> str:
    """Route the official tool_call object to the right function."""
    name = tool_call.function.name
    
    # The SDK guarantees this is a JSON string, so we just load it
    arguments = json.loads(tool_call.function.arguments)
    
    if name == "get_weather":
        result = get_weather(**arguments)
    elif name == "calculate":
        result = calculate(**arguments)
    else:
        result = {"error": f"Unknown tool {name}"}
        
    return json.dumps(result)

# ---------------------------------------------------------------------------
# 4. The Official Agent Loop
# ---------------------------------------------------------------------------

def run_agent(user_message: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant with access to tools."},
        {"role": "user", "content": user_message}
    ]

    for iteration in range(6):
        # We pass our schema directly into the `tools` parameter!
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=my_tools  
        )
        
        message = response.choices[0].message
        messages.append(message) # Append the AI's response to history
        
        # Did the AI ask for a tool? (The SDK handles the checking for us!)
        if message.tool_calls:
            for tool_call in message.tool_calls:
                # 1. Run the tool
                result_str = dispatch(tool_call)
                
                # 2. Append the official tool result message format
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_str
                })
        else:
            # If there are no tool_calls, the AI is done and giving us a final text answer!
            return message.content
            
    return "Iteration limit reached."

# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_queries = [
        "What is the weather in Tokyo right now?",
        "If I have 15 boxes with 24 apples in each, how many apples do I have in total?",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        result = run_agent(query)
        print(f"\nAnswer: {result}")