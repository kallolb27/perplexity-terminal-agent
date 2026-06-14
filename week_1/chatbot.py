import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ChatAgent:
    def __init__(self, model_name="openrouter/free", max_turns=5):
        """
        Constructs the chatbot as a Python Class with configuration options.
        - model_name: Allows switching models dynamically.
        - max_turns: The rolling buffer limit (keeps only the last N turns).
        """
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
        )
        self.model_name = model_name
        self.max_turns = max_turns
        
        # Initialize conversation state with the system prompt
        self.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    def chat(self, user_message: str) -> str:
        """Processes a single turn of conversation[cite: 8]."""
        # 1. Enforce rolling buffer (drop oldest user/assistant pair if over limit)[cite: 8]
        # Note: self.messages[0] is our system prompt, we don't want to drop that![cite: 8]
        # Total turns = (total length - 1 system prompt) / 2
        current_turns = (len(self.messages) - 1) // 2
        if current_turns >= self.max_turns:
            # Drop the oldest user message and assistant reply (indices 1 and 2)[cite: 8]
            del self.messages[1:3]
            print("\n[System: Trimmed oldest turn from rolling buffer to save context budget]\n")

        # 2. Append new user message[cite: 8]
        self.messages.append({"role": "user", "content": user_message})

        # 3. Call the API sending the history[cite: 8]
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages,
        )

        # 4. Extract and save response[cite: 8]
        reply = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})
        return reply

def run_menu_and_chat():
    print("--- Select Your Model ---")
    print("1. Automatic Free Router (Recommended)")
    print("2. Paid DeepSeek Flash (If you have balance)")
    choice = input("Select option (1 or 2): ").strip()
    
    selected_model = "openrouter/free" if choice != "2" else "deepseek/deepseek-v4-flash"
    
    # Initialize the class with a max buffer of 3 turns to see it trim live[cite: 8]
    agent = ChatAgent(model_name=selected_model, max_turns=3)
    
    print(f"\nChat started using model: {selected_model}. Type 'exit' to quit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
            
        reply = agent.chat(user_input)
        print(f"\nAI: {reply}\n")

if __name__ == "__main__":
    run_menu_and_chat()