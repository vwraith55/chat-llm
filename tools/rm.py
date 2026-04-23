import os
import glob
import git
from tools.safe_path import is_path_safe


def rm(path):
    """
    Delete file(s) matching the given path or glob pattern and commit the changes.

    >>> rm('/etc/passwd')
    'Error: unsafe path'
    >>> rm('../secret.txt')
    'Error: unsafe path'
    >>> rm('nonexistent_file_xyz.txt')
    'Error: no files found matching nonexistent_file_xyz.txt'
    """
    if not is_path_safe(path):
        return 'Error: unsafe path'

    matches = glob.glob(path)
    if not matches:
        return f'Error: no files found matching {path}'

    for match in matches:
        os.remove(match)

    repo = git.Repo('.')
    try:
        repo.index.remove(matches, force=True)
    except Exception:
        pass
    repo.index.commit(f'[docchat] rm {path}')

    return f'Successfully deleted {len(matches)} file(s): {", ".join(matches)}'


rm_tool_def = {
    "type": "function",
    "function": {
        "name": "rm",
        "description": "Delete file(s) matching a path or glob pattern and commit the changes.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path or glob pattern of file(s) to delete.",
                }
            },
            "required": ["path"],
        },
    },
}
