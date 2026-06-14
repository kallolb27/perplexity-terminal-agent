"""
Build 3: Extend Your Week 1 Chatbot into a TUI
===============================================
Take the multi-turn chatbot you built in Week 1 and give it a full-screen terminal UI
using Textual. The chat logic stays the same; you're just changing the interface.

Requirements:
  - A scrollable chat log that shows conversation history
  - An input box at the bottom for the user to type
  - Keyboard shortcuts:
      Ctrl+L  →  clear the chat display (not the conversation history)
      Ctrl+K  →  compact: clear conversation history too (fresh start)
      Ctrl+Q  →  quit the application
  - Messages displayed with clear role labels: [You] and [Agent]
  - The UI must not freeze while waiting for an API response

Stretch goals:
  - Show the model name and token count in the Header or Footer
  - Add a Ctrl+S binding to save the conversation to a text file
  - Display a "thinking..." indicator while the API call is in progress

Important: API calls are blocking. Use run_worker(thread=True) to keep the UI alive
while waiting for responses. See Lesson 4 for the pattern.
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Input, RichLog
from textual.containers import Container

load_dotenv()

# Set up our standard OpenRouter pipeline
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

class SimpleChatApp(App):
    """A beautiful, full-screen terminal interface for our chatbot."""
    
    # 1. Define the layout styling right inside the code using CSS rules
    CSS = """
    Container {
        layout: vertical;
        padding: 1;
    }
    RichLog {
        height: 1fr;
        border: solid $primary;
        background: $background;
        margin-bottom: 1;
    }
    Input {
        dock: bottom;
        height: 3;
        border: dashed $secondary;
    }
    """

    # 2. Bind physical keyboard keys to app actions
    BINDINGS = [
        Binding("ctrl+l", "clear_display", "Clear Screen"),
        Binding("ctrl+k", "clear_history", "Fresh Restart"),  # <-- ADD THIS LINE
        Binding("ctrl+q", "quit", "Quit Application"),
    ]

    def compose(self) -> ComposeResult:
        """Constructs the visual widget layout of the app."""
        yield Header(show_clock=True)
        with Container():
            # RichLog is a highly performance-optimized scrolling box for text markup
            yield RichLog(id="chat-box", wrap=True, markup=True)
            yield Input(placeholder="Type your message here and press Enter...")
        yield Footer()

    def on_mount(self) -> None:
        """Runs automatically the split second the app boots up on screen."""
        self.chat_box = self.query_one("#chat-box", RichLog)
        self.chat_box.write("[bold cyan]🤖 TUI Interface Active. Say hello![/bold cyan]\n")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Triggers immediately when you hit 'Enter' inside the text input field."""
        user_text = event.value.strip()
        
        if not user_text:
            return

        # 1. Write the user's message to the display box immediately
        self.chat_box.write(f"[bold blue]You:[/bold blue] {user_text}")
        
        # 2. Clear out the typing box so you can type the next message
        event.input.clear()

        # 3. Use an async worker thread to call OpenRouter so the screen doesn't freeze!
        self.run_worker(self.fetch_ai_response(user_text), thread=True)

    async def fetch_ai_response(self, user_message: str):
        """Worker thread that talks to the API safely in the background."""
        try:
            response = client.chat.completions.create(
                model="openrouter/free",
                messages=[{"role": "user", "content": user_message}]
            )
            reply = response.choices[0].message.content
            
            # Write the result back to our UI display panel
            self.call_from_thread(self.chat_box.write, f"[bold green]AI:[/bold green] {reply}\n")
        except Exception as e:
            self.call_from_thread(self.chat_box.write, f"[red]Error: {str(e)}[/red]\n")

    def action_clear_screen(self) -> None:
        """The action bound to Ctrl+L."""
        self.chat_box.clear()
        self.chat_box.write("[dim]Display cleared.[/dim]\n")
    
    def action_clear_history(self) -> None:
        """Ctrl+K: Wipe the display clean."""
        self.chat_log.clear()
        self.tool_log.clear()
        self.chat_log.write("[bold cyan]🧹 History wiped clean. App restarted.[/bold cyan]\n")


if __name__ == "__main__":
    app = SimpleChatApp()
    app.run()