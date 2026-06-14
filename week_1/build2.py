import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# We set up the client exactly like we did in build1
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

def run_chatbot():
    # Week 1 rule: Start with a system message to set the assistant's behavior
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

    print("Chat started. Type 'exit' or 'quit' to end the session.\n")

    while True:
        # 1. Take input from the user in the terminal
        user_input = input("You: ")
        
        # 2. Check if the user wants to leave the loop
        if user_input.strip().lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
            
        # Stretch goal: Add a reset command to test context loss live
        if user_input.strip().lower() == "/reset":
            messages = [{"role": "system", "content": "You are a helpful assistant."}]
            print("\n--- System: Chat history wiped! The AI now has amnesia. ---\n")
            continue

        # 3. Append the user's message to our running history list
        messages.append({"role": "user", "content": user_input})

        # 4. Call the API with our auto-routing free model, sending the WHOLE list
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
        )

        # 5. Extract just the text from the response object
        assistant_reply = response.choices[0].message.content

        # 6. Append the assistant's reply to messages so it remembers next turn
        messages.append({"role": "assistant", "content": assistant_reply})

        # 7. Print the reply nicely for the user
        print(f"\nAI: {assistant_reply}\n")

if __name__ == "__main__":
    run_chatbot()