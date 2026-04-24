import git
import subprocess
import tempfile
import os
from tools.safe_path import is_path_safe
from tools.doctests import doctests


def apply_diff(path, diff):
    """
    Apply a diff to a file using wiggle.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.diff', delete=False) as f:
        f.write(diff)
        diff_path = f.name
    try:
        result = subprocess.run(
            ['wiggle', '--replace', path, diff_path],
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout + result.stderr
    finally:
        os.unlink(diff_path)


def write_files(files, commit_message):
    """
    Write multiple files and commit them to git.

    >>> write_files([{'path': 'test_write.txt', 'contents': 'hello'}], 'test commit')
    'Successfully wrote and committed 1 file(s).'
    >>> import os; os.remove('test_write.txt')
    >>> write_files([{'path': '/etc/passwd', 'contents': 'bad'}], 'test')
    'Error: unsafe path /etc/passwd'
    """
    for file in files:
        path = file['path']
        if not is_path_safe(path):
            return f'Error: unsafe path {path}'
        if 'diff' in file:
            success, wiggle_output = apply_diff(path, file['diff'])
            if not success:
                return f'Error applying diff to {path}: {wiggle_output}'
        else:
            contents = file.get('contents', '')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(contents)

    repo = git.Repo('.')
    for file in files:
        repo.index.add([file['path']])
    repo.index.commit(f'[docchat] {commit_message}')

    output = f'Successfully wrote and committed {len(files)} file(s).'
    for file in files:
        if file['path'].endswith('.py'):
            output += '\n' + doctests(file['path'])
    return output


def write_file(path, contents=None, commit_message='', diff=None):
    """
    Write a file and commit it to git.

    >>> write_file('test_write2.txt', 'hello', 'test commit')
    'Successfully wrote and committed 1 file(s).'
    >>> import os; os.remove('test_write2.txt')
    >>> write_file('/etc/passwd', 'bad', 'test')
    'Error: unsafe path /etc/passwd'
    """
    file_dict = {'path': path}
    if diff is not None:
        file_dict['diff'] = diff
    else:
        file_dict['contents'] = contents
    return write_files([file_dict], commit_message)


write_file_tool_def = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write a file and commit it to git.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write.",
                },
                "contents": {
                    "type": "string",
                    "description": "Full contents to write to the file.",
                },
                "commit_message": {
                    "type": "string",
                    "description": "Git commit message describing the change.",
                }
            },
            "required": ["path", "contents", "commit_message"],
        },
    },
}


write_files_tool_def = {
    "type": "function",
    "function": {
        "name": "write_files",
        "description": "Write or patch multiple files and commit them to git.",
        "parameters": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "description": "List of dictionaries with path and either contents or diff keys.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "contents": {"type": "string"},
                            "diff": {"type": "string"},
                        }
                    }
                },
                "commit_message": {
                    "type": "string",
                    "description": "Git commit message describing the changes.",
                }
            },
            "required": ["files", "commit_message"],
        },
    },
}
