"""
Web search and fetch tools — carry forward from Week 2.

Implement or copy from your week_2/project/:
  - web_search(query) — Serper
  - web_fetch(url) — requests + trafilatura/markdownify
"""

# TODO: copy from Week 2 project
import os
import xml.etree.ElementTree as ET
import json
import requests
import trafilatura
from dotenv import load_dotenv
from openai import OpenAI
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Input, RichLog
from textual.containers import Horizontal

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

# --- STABLE PRODUCTION TOOLS ---

def web_search(query: str, num_results: int = 4) -> str:
    """Search Google using Serper.dev and return live result snippets."""
    if not SERPER_API_KEY:
        return "Error: SERPER_API_KEY is not set in your .env file."
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": query, "num": num_results},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        
        # Safety Guard: If API returned empty data or invalid JSON format
        if not data or not isinstance(data, dict):
            return "No live search results found (Invalid or empty API response)."
        
        results = []
        
        # Check if Google gave us a direct Answer Box
        if "answerBox" in data:
            answerBox = data.get("answerBox", {})
            if isinstance(answerBox, dict):
                answer = answerBox.get("answer") or answerBox.get("snippet")
                if answer:
                    results.append(f"DIRECT ANSWER BOX: {answer}\n---")
                
        for item in data.get("organic", []):
            if isinstance(item, dict):
                results.append(f"Title: {item.get('title')}\nURL: {item.get('link')}\nSnippet: {item.get('snippet')}\n---")
                
        return "\n".join(results) if results else "No live search results found."
    except Exception as e:
        return f"Error during live search execution: {str(e)}"

def web_fetch(url: str) -> str:
    """Fetch a real URL, scrape the main text body, and truncate cleanly."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"}
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        response.raise_for_status()
        
        text = trafilatura.extract(response.text, include_comments=False, include_tables=True)
        if not text:
            return "Error: Could not extract readable text body from this webpage."
            
        return text[:6000] + "\n\n[...Content truncated to save context budget...]" if len(text) > 6000 else text
    except Exception as e:
        return f"Error trying to fetch webpage: {str(e)}"

# ==========================================
# TOOL SCHEMAS FOR THE AGENT
# ==========================================

WEB_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current events, blogs, and documentation. Use this when paper_search is not appropriate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Fetch and read the full text of a webpage from a URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The full URL of the webpage to read"}
                },
                "required": ["url"]
            }
        }
    }
]    