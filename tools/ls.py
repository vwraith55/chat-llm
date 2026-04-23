"""Tool for listing files in a directory."""

import glob
from tools.safe_path import is_path_safe


ls_tool_def = {
    "type": "function",
    "function": {
        "name": "ls",
        "description": "List files in a directory. Defaults to the current directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The directory path to list. Defaults to '.'",
                }
            },
            "required": [],
        },
    },
}


def ls(path=None):
    """
    List files in the given directory, sorted asciibetically.
    Returns an error string if the path is unsafe (absolute or traversal).

    >>> 'cat.py' in ls('tools')
    True
    >>> 'steak.png' in ls('tools')
    True
    >>> ls('/etc')
    'Error: unsafe path'
    >>> ls('../secret')
    'Error: unsafe path'
    >>> ls('nonexistent_folder_xyz')
    ''
    """
    if not is_path_safe(path):
        return "Error: unsafe path"
    files = sorted(glob.glob(f"{path}/*"))
    # Strip leading path prefix for cleaner output
    files = [f.replace(f"{path}/", "", 1) if path != "." else f.lstrip("./") for f in files]
    return "\n".join(files)
