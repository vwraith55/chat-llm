import subprocess

def doctests(path):
    """
    Run doctests on a python file and return the output.

    >>> 'ok' in doctests('tools/safe_path.py')
    True
    >>> 'Error: unsafe path' in doctests('/etc/passwd')
    True
    """
    from tools.safe_path import is_path_safe
    if not is_path_safe(path):
        return 'Error: unsafe path'
    result = subprocess.run(
        ['python3', '-m', 'doctest', path, '-v'],
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr

doctests_tool_def = {
    "type": "function",
    "function": {
        "name": "doctests",
        "description": "Run doctests on a python file and return the output.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the python file to run doctests on.",
                }
            },
            "required": ["path"],
        },
    },
}