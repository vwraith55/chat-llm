"""Tool for compacting the chat history into a brief summary."""

from groq import Groq


def compact(messages):
    """
    Summarize a list of chat messages into 1-5 lines using a subagent.

    Returns a summary string of the conversation.

    >>> summary = compact([{'role': 'user', 'content': 'my name is bob'},
    ...                    {'role': 'assistant', 'content': 'Hi bob!'}])
    >>> isinstance(summary, str)
    True
    >>> len(summary) > 0
    True
    """
    client = Groq()
    history = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in messages
        if isinstance(m.get('content'), str)
    )
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": f"Summarize this conversation in 1-5 lines:\n\n{history}",
            }
        ],
    )
    return response.choices[0].message.content
