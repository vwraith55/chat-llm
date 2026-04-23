import subprocess


def pip_install(library_name):
    """
    Install a Python library using pip3.

    >>> 'Successfully installed' in pip_install('cowsay') or 'already satisfied' in pip_install('cowsay').lower()
    True
    >>> pip_install('../malicious')
    'Error: unsafe library name'
    """
    if library_name.startswith('/') or '..' in library_name:
        return 'Error: unsafe library name'
    result = subprocess.run(
        ['pip3', 'install', library_name],
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr


pip_install_tool_def = {
    "type": "function",
    "function": {
        "name": "pip_install",
        "description": "Install a Python library using pip3.",
        "parameters": {
            "type": "object",
            "properties": {
                "library_name": {
                    "type": "string",
                    "description": "The name of the library to install.",
                }
            },
            "required": ["library_name"],
        },
    },
}
