# Research Desk: Agentic AI Workspace

## Overview
Research Desk is a fully functional, terminal-based AI research assistant. It leverages an autonomous LLM loop to execute multi-step research tasks, maintain persistent memory across sessions, interact with the local file system within a secure sandbox, and scrape live data from the internet and academic databases. 

The application features a split-pane **Textual User Interface (TUI)** that separates human-agent chat from backend tool execution logs, providing a transparent and professional user experience.

---

## System Architecture

The project is structured with a modular, separation-of-concerns architecture:

* **The Brain (`agent.py`):** The core LLM loop powered by `google/gemini-2.5-flash:free` (via OpenRouter). It handles tool dispatching, maximum iteration limits, and context window management.
* **The Memory (`sessions.py`):** A database-like session manager. It auto-generates human-readable titles for conversations, saves chat histories as unique JSON files in a hidden `.agent/sessions/` directory, and automatically loads the most recent context on boot.
* **The Face (`tui.py`):** A full-screen graphical dashboard built with the `textual` library. It inherits the core Agent logic and maps tool execution events directly to a visual sidebar without freezing the UI thread.
* **The Hands (`tools/`):** A centralized switchboard (`__init__.py`) that bundles three distinct tool modules:
    * **`files.py`:** Sandboxed workspace tools (`read_file`, `write_file`, `edit_file`, `list_files`) with strict boundary resolution and paginated reading to protect context limits.
    * **`web.py`:** Live internet tools using the **Serper API** for searching and **Trafilatura/Markdownify** for clean, ad-free article extraction.
    * **`papers.py`:** Academic research tools integrating the **Hugging Face Papers API**, equipped with automatic arXiv ID normalization and fallback protocols for unindexed papers.

---

## Setup Guide

### 1. Prerequisites
Ensure you have Python 3 installed on your machine. 

### 2. Install Dependencies
Install the required libraries by running the following command in your terminal:
```bash
pip install openai python-dotenv requests markdownify trafilatura textual