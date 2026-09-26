import ollama

# conversation_history = [
#     {"role": "system", "content": "You are a food ordering assistant."}
# ]

conversation_history = [
{
"role": "system",
"content": """
You are a helpful AI food ordering assistant.

Rules for responses:
1. Always format answers clearly.
2. Use bullet points when listing items.
3. Use short paragraphs.
4. If asking questions, present them as numbered points.
5. Be concise and friendly.

Example format:

Sure! I can help with that.

To recommend restaurants, I need a little information:

1. Cuisine preference (Indian, Chinese, Italian, etc.)
2. Price range (budget / moderate / premium)
3. Dining style (casual / fine dining)
4. Dietary preferences (vegetarian, vegan, etc.)
"""
}
]



def chat_with_llm(user_prompt):

    conversation_history.append({
        "role": "user",
        "content": user_prompt
    })

    response = ollama.chat(
        model="llama3.1",
        messages=conversation_history
    )

    reply = response["message"]["content"]

    conversation_history.append({
        "role": "assistant",
        "content": reply
    })

    return reply