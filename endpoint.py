'''
A basic openai-compatible endpoint for serving model responses.
'''

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

from chat import Chat

app = FastAPI()


@app.api_route("/", methods=["GET", "POST"], response_class=HTMLResponse)
async def english():
    return 'hello world\n'


@app.api_route("/spanish", methods=["GET", "POST"], response_class=HTMLResponse)
async def spanish():
    return 'hola mundo\n'


@app.api_route("/latin", methods=["GET", "POST"], response_class=HTMLResponse)
async def latin():
    return 'salve munde\n'


@app.api_route("/v1/chat/completions", methods=["GET", "POST"])
async def chat_completions(request: dict) -> dict:
    messages = request.get("messages", [])

    chat = Chat()

    if len(messages) > 1:
        chat.messages.extend(messages[:-1])

    last_message = messages[-1] if messages else {"role": "user", "content": ""}
    last_content = last_message.get("content", "")
    if isinstance(last_content, list):
        text_parts = []
        for item in last_content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        last_content = "\n".join(text_parts)

    response_content = chat.send_message(last_content)

    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 0,
        "model": request.get("model", chat.MODEL),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
