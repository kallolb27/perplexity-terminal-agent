"""
Paper search and read tools — Hugging Face Papers API (arXiv index).

Implement:
  - paper_search(query, limit) -> {papers: [{arxiv_id, title, abstract, url}, ...]}
  - read_paper(arxiv_id) -> {title, abstract, content, url, ...}

API docs: week_3/3_paper_tools.md
"""
import os
import re
import requests

def get_hf_headers() -> dict:
    """Helper to attach the HF_TOKEN if the user added it to their .env file."""
    headers = {}
    token = os.environ.get("HF_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def paper_search(query: str, limit: int = 5) -> dict:
    """Search Hugging Face Papers index for ML/CS papers."""
    url = "https://huggingface.co/api/papers/search"
    params = {"q": query, "limit": limit}
    
    try:
        resp = requests.get(url, params=params, headers=get_hf_headers())
        resp.raise_for_status()
        results = resp.json()
        
        papers = []
        for item in results:
            # The API sometimes wraps paper data in a "paper" key, we handle both shapes
            paper_data = item.get("paper", item) 
            papers.append({
                "arxiv_id": paper_data.get("id"),
                "title": paper_data.get("title"),
                "summary": paper_data.get("summary", "")[:250] + "...", # Small snippet for context
                "url": f"https://arxiv.org/abs/{paper_data.get('id')}"
            })
        return {"papers": papers} if papers else {"content": "No papers found on Hugging Face for this query."}
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

def read_paper(arxiv_id: str) -> dict:
    """Fetch paper metadata and markdown content using an arXiv ID."""
    # 1. Normalize the ID (Extract "2205.14135" even if passed as a full URL)
    match = re.search(r"(\d{4}\.\d{4,5}(?:v\d+)?)", arxiv_id)
    if not match:
        return {"error": f"Could not extract a valid arXiv ID from '{arxiv_id}'"}
    clean_id = match.group(1)

    try:
        # 2. Fetch the metadata
        meta_url = f"https://huggingface.co/api/papers/{clean_id}"
        meta_resp = requests.get(meta_url, headers=get_hf_headers())
        
        # Explicit 404 handling so the AI knows to use web_fetch instead
        if meta_resp.status_code == 404:
            return {"error": "404 Not Found: This paper exists but is not indexed on Hugging Face yet. Please fall back to web_fetch on the arXiv URL."}
        meta_resp.raise_for_status()
        meta = meta_resp.json()

        # 3. Fetch the Markdown content
        md_url = f"https://huggingface.co/papers/{clean_id}.md"
        md_resp = requests.get(md_url, headers=get_hf_headers())
        content = md_resp.text if md_resp.status_code == 200 else "Markdown content not available for this paper."

        # 4. Truncate massive papers to protect the context window
        max_chars = 45000 
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n...[CONTENT TRUNCATED FOR LENGTH]"

        return {
            "arxiv_id": clean_id,
            "title": meta.get("title"),
            "published_at": meta.get("publishedAt"),
            "abstract": meta.get("summary"),
            "content": content,
            "url": f"https://arxiv.org/abs/{clean_id}"
        }
    except Exception as e:
        return {"error": f"Failed to read paper: {str(e)}"}

# ==========================================
# TOOL SCHEMAS FOR THE AGENT
# ==========================================

PAPER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "paper_search",
            "description": "Search Hugging Face Papers index for ML/CS papers. Use this for literature reviews.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keywords"},
                    "limit": {"type": "integer", "description": "Max results to return (default 5)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_paper",
            "description": "Fetch paper metadata and markdown content using an arXiv ID. Always use this after paper_search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "arxiv_id": {"type": "string", "description": "The arXiv ID (e.g., 2205.14135)"}
                },
                "required": ["arxiv_id"]
            }
        }
    }
]