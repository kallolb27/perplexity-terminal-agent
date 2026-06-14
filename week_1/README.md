# Week 1 Submission

## Implementation Details
I implemented a robust multi-turn chatbot using the OpenRouter API. The core of my implementation relies on wrapping the chat sequence inside a clean, reusable Python class called `ChatAgent`. 

Because LLM APIs are completely stateless, I managed the conversation state locally by appending all user inputs and assistant replies to an in-memory `messages` array, passing the entire array on every subsequent API endpoint call.

## Design Decisions & Buffer Management
To prevent our conversation from growing infinitely and consuming massive amounts of context tokens, I built a rolling buffer truncation strategy. By monitoring the length of the message array, the agent automatically drops the oldest user/assistant chat pair once the conversation exceeds the configured maximum turns, while preserving the foundational system message at index 0. This keeps calls performant and predictable.