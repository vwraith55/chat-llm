"""Tool for searching file contents using regular expressions."""

import re
import glob
from tools.safe_path import is_path_safe


grep_tool_def = {
    "type": "function",
    "function": {
        "name": "grep",
        "description": "Search for lines matching a regex across files matching a glob pattern.",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "A regular expression to search for.",
                },
                "path_glob": {
                    "type": "string",
                    "description": "A file path or glob pattern (e.g. '*.py' or 'src/*.txt').",
                },
            },
            "required": ["pattern", "path_glob"],
        },
    },
}


def grep(pattern, path_glob):
    """
    Search for lines matching a regex in all files matching the glob pattern.

    Returns matching lines as a newline-joined string, or empty string if no matches.
    Returns an error string if the path is unsafe.

    >>> import os
    >>> with open('_test_grep_tmp.txt', 'w') as f:
    ...     _ = f.write('hello world\\nfoo bar\\nhello again')
    >>> grep('hello', '_test_grep_tmp.txt')
    'hello world\\nhello again'
    >>> grep('xyz', '_test_grep_tmp.txt')
    ''
    >>> os.unlink('_test_grep_tmp.txt')
    >>> grep('hello', '/etc/passwd')
    'Error: unsafe path'
    >>> grep('hello', '../outside/*.txt')
    'Error: unsafe path'
    >>> with open('_test_grep_bad.bin', 'wb') as f:
    ...     _ = f.write(bytes.fromhex('80818283'))
    >>> grep('hello', '_test_grep_bad.bin')
    ''
    >>> os.unlink('_test_grep_bad.bin')
    >>> os.mkdir('_test_grep_dir')
    >>> grep('hello', '_test_grep_dir')
    ''
    >>> os.rmdir('_test_grep_dir')
    """
    if not is_path_safe(path_glob):
        return "Error: unsafe path"

    matching_lines = []
    for filepath in sorted(glob.glob(path_glob)):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if re.search(pattern, line):
                        matching_lines.append(line.rstrip("\n"))
        except (UnicodeDecodeError, IsADirectoryError, PermissionError):
            continue

    return "\n".join(matching_lines)
