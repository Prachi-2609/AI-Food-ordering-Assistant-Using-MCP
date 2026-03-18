# test_llm.py

from llm_agent import chat_with_llm

while True:
    user_input = input("You: ")
    response = chat_with_llm(user_input)
    print("Bot:", response)
    if user_input.lower() == "exit":
        break