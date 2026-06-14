import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

def call_model(prompt: str) -> str:
    """
    Make a single chat completion call.
    Print the full response object first and understand its structure.
    Then return just the assistant's text.
    """
    # 1. We make the API call using the free deepseek flash model
    response = client.chat.completions.create(
        model="openrouter/free",  # <-- CHANGED TO THE AUTO-ROUTER
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    
    # 2. Print the raw response object to inspect its structure
    print("\n--- DEBUG: FULL RESPONSE OBJECT ---")
    print(response)
    print("------------------------------------\n")
    
    # 3. Extract and return just the assistant's text
    return response.choices[0].message.content

if __name__ == "__main__":
    print("Sending question...")
    result = call_model("What is the capital of Australia?")
    print("Final Model Reply:")
    print(result)