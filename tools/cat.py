"""Tool for reading the contents of a file."""

from tools.safe_path import is_path_safe


cat_tool_def = {
    "type": "function",
    "function": {
        "name": "cat",
        "description": "Read and return the contents of a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to read.",
                }
            },
            "required": ["path"],
        },
    },
}


def cat(path):
    """
    Read and return the contents of a file as a string.

    Returns an error string if the path is unsafe or the file cannot be read.

    >>> import os
    >>> with open('_test_cat_tmp.txt', 'w') as f:
    ...     _ = f.write('hello world')
    >>> cat('_test_cat_tmp.txt')
    'hello world'
    >>> os.unlink('_test_cat_tmp.txt')
    >>> cat('/etc/passwd')
    'Error: unsafe path'
    >>> cat('../outside.txt')
    'Error: unsafe path'
    >>> cat('nonexistent_file_xyz.txt')
    'Error: file not found'
    >>> with open('_test_bad.bin', 'wb') as f:
    ...     _ = f.write(bytes.fromhex('80818283'))
    >>> cat('_test_bad.bin')
    'Error: could not decode file'
    >>> os.unlink('_test_bad.bin')
    """
    if not is_path_safe(path):
        return 'Error: unsafe path'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return 'Error: file not found'
    except UnicodeDecodeError:
        return 'Error: could not decode file'
