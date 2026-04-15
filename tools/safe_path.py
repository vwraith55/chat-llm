"""Shared helper for validating that file paths are safe to access."""


def is_path_safe(path):
    """
    Return True if the path is safe (not absolute and contains no directory traversal).

    >>> is_path_safe('.')
    True
    >>> is_path_safe('some/relative/path.txt')
    True
    >>> is_path_safe('/etc/passwd')
    False
    >>> is_path_safe('../secret')
    False
    >>> is_path_safe('some/../sneaky')
    False
    >>> is_path_safe('')
    True
    """
    if path.startswith("/"):
        return False
    if ".." in path.split("/"):
        return False
    return True
