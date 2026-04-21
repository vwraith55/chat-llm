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
    >>> import os
    >>> with open('_test_image.jpg', 'wb') as f:
    ...     _ = f.write(bytes.fromhex('ffd8ffe0'))
    >>> messages = []
    >>