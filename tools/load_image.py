"""Tool for loading a local image file into the chat context."""

import base64
from tools.safe_path import is_path_safe

load_image_tool_def = {
    "type": "function",
    "function": {
        "name": "load_image",
        "description": "Load a local image file so the LLM can analyze it.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the image file.",
                }
            },
            "required": ["path"],
        },
    },
}


def load_image(path, messages):
    """
    Load a local image and add it to the chat messages list.
    Returns a confirmation string or error message.

    >>> load_image('/etc/passwd', [])
    'Error: unsafe path'
    >>> load_image('../outside.jpg', [])
    'Error: unsafe path'
    >>> load_image('nonexistent.jpg', [])
    'Error: file not found'
    >>> messages = []
    >>> load_image('tools/steak.png', messages)
    'Image tools/steak.png loaded successfully.'
    >>> len(messages) == 1
    True
    """
    if path is None:
        return 'Usage: /load_image <path>'
    if messages is None:
        messages = []
    if not is_path_safe(path):
        return 'Error: unsafe path'
    try:
        with open(path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        return 'Error: file not found'

    ext = path.split('.')[-1].lower()
    media_type = f'image/{ext}' if ext != 'jpg' else 'image/jpeg'

    messages.append({
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{media_type};base64,{image_data}"
                }
            }
        ]
    })
    return f'Image {path} loaded successfully.'
