# Perplexity Research Terminal Online

An autonomous, terminal-based AI research assistant. This project demonstrates how to connect a Large Language Model to the physical internet using custom Python tools, SDK tool-calling, and a multi-threaded Textual UI.

## 🎯 Objectives Achieved
* **Autonomous Tool Calling:** The AI intelligently decides when to use Google Search versus when to scrape a specific URL for deep reading.
* **Live Web Integration:** * Integrated **Serper.dev** to bypass training data cutoffs and fetch real-time facts/weather (including Direct Answer Box extraction).
  * Integrated **Trafilatura** for clean, ad-free web text extraction with a 6,000-character context budget limit.
* **Parallel Execution:** Capable of executing multiple tool requests (e.g., searching three different cities) simultaneously in a single turn.
* **Persistent Memory State:** Implemented a continuous `conversation_history` array that allows the AI to remember user names and context across the session.
* **Multi-Threaded UI:** Built a stateful Terminal User Interface (TUI) using `Textual`. Background worker threads ensure the UI never freezes while the AI waits for network responses.
* **Production Error Handling:** Added robust crash guards against `NoneType` data, 504 Gateway Timeouts, and empty API responses.
* **Live Token Tracking:** Intercepts LLM usage receipts to display real-time session token costs in the tool log.

## ⌨️ TUI Controls & Key Bindings
To prevent key-binding conflicts with IDE terminals (like VS Code), the standard TUI controls have been explicitly remapped to the Function and Escape keys:

* **`F1`** : **Clear Screen** (Wipes the visual logs but keeps the AI's memory intact).
* **`F2`** : **Wipe Memory** (Completely resets the conversation history array and zeroes out the token counter for a fresh start).
* **`Escape`** : **Quit** (Safely terminates the application and background threads).

## 🚀 Built With
* Python
* Textual (TUI framework)
* OpenRouter API (LLM Routing)
* Serper API (Google Search)