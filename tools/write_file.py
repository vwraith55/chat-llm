import git
from tools.safe_path import is_path_safe
from tools.doctests import doctests

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
        contents = file['contents']
        if not is_path_safe(path):
            return f'Error: unsafe path {path}'
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


def write_file(path, contents, commit_message):
    """
    Write a file and commit it to git.

    >>> write_file('test_write2.txt', 'hello', 'test commit')
    'Successfully wrote and committed 1 file(s).'
    >>> import os; os.remove('test_write2.txt')
    >>> write_file('/etc/passwd', 'bad', 'test')
    'Error: unsafe path /etc/passwd'
    """
    return write_files([{'path': path, 'contents': contents}], commit_message)

write_file_tool_def = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write contents to a file and commit it to git.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write.",
                },
                "contents": {
                    "type": "string",
                    "description": "Contents to write to the file.",
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
        "description": "Write multiple files and commit them to git.",
        "parameters": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "description": "List of dictionaries with path and contents keys.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "contents": {"type": "string"}
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