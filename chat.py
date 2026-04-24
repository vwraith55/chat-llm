
import json
import os
from groq import Groq
from dotenv import load_dotenv

from tools.calculate import calculate, calculate_tool_def
from tools.ls import ls, ls_tool_def
from tools.cat import cat, cat_tool_def
from tools.grep import grep, grep_tool_def
from tools.compact import compact
import readline
import glob
from tools.load_image import load_image, load_image_tool_def
from tools.doctests import doctests, doctests_tool_def
from tools.write_file import write_file, write_files, write_file_tool_def, write_files_tool_def
from tools.rm import rm, rm_tool_def
from tools.pip_install import pip_install, pip_install_tool_def

TOOLS = [
    calculate_tool_def,
    ls_tool_def,
    cat_tool_def,
    grep_tool_def,
    load_image_tool_def,
    doctests_tool_def,
    write_file_tool_def,
    write_files_tool_def,
    rm_tool_def,
    pip_install_tool_def,
]

AVAILABLE_FUNCTIONS = {
    "calculate": calculate,
    "ls": ls,
    "cat": cat,
    "grep": grep,
    "load_image": load_image,
    "doctests": doctests,
    "write_file": write_file,
    "write_files": write_files,
    "rm": rm,
    "pip_install": pip_install,
}

load_dotenv()


class Chat:
    """
    A conversational AI agent that maintains message history and supports tool use.

    The agent can call tools automatically when needed, or the user can invoke
    tools manually using slash commands (e.g. /ls, /cat, /grep).

    >>> chat = Chat()
    >>> result = chat.send_message('my name is bob. do not use any tools to answer this.', temperature=0.0)
    >>> 'bob' in result.lower()
    True
    >>> result2 = chat.send_message('what is my name? do not use any tools to answer this.', temperature=0.0)
    >>> 'bob' in result2.lower()
    True
    >>> chat2 = Chat()
    >>> result3 = chat2.send_message('what is my name? do not use any tools to answer this.', temperature=0.0)
    >>> 'bob' in result3.lower()
    False
    """

    client = Groq()

    def __init__(self, debug=False):
        self.debug = debug
        self.MODEL = "llama-3.3-70b-versatile"
        self.VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. "
                    "Answer in 1-2 sentences. "
                    "You have tools to read files in the current directory."
                ),
            }
        ]

    def send_message(self, message, temperature=0.8):
        """
        Send a message to the LLM and return its response, handling any tool calls.

        >>> chat = Chat()
        >>> result = chat.send_message('say only the word hello', temperature=0.0)
        >>> 'hello' in result.lower()
        True
        """
        self.messages.append({"role": "user", "content": message})
        has_images = any(
            isinstance(m.get('content'), list)
            for m in self.messages
        )
        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            model=self.VISION_MODEL if has_images else self.MODEL,
            temperature=temperature,
            seed=0,
            tools=TOOLS,
            tool_choice="auto",
        )
        response_message = chat_completion.choices[0].message
        tool_calls = response_message.tool_calls
        if tool_calls:
            # Add assistant's tool-use message to history
            self.messages.append({
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": response_message.tool_calls,
            })
            doctest_failed = False
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)
                self.messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    }
                )
                # Check if doctests failed after writing a python file
                if function_name in ('write_file', 'write_files'):
                    if 'failed' in str(function_response).lower():
                        doctest_failed = True
            # Ralph Wiggum loop: force another round if doctests failed
            if doctest_failed:
                self.messages.append({
                    "role": "user",
                    "content": "Your doctests failed. Please fix the code and try again."
                })
                return self.send_message('', temperature=temperature)
            # Get final response after tool use
            second_response = self.client.chat.completions.create(
                messages=self.messages,
                model=self.MODEL,
                temperature=temperature,
                seed=0,
            )
            result = second_response.choices[0].message.content
        else:
            result = response_message.content
        self.messages.append({"role": "assistant", "content": result})
        return result

    def run_tool_manually(self, command, args):
        """
        Run a tool manually and append its output to message history as a tool result.

        >>> chat = Chat()
        >>> 'chat.py' in chat.run_tool_manually('ls', ['.'])
        True
        >>> 'README.md' in chat.run_tool_manually('ls', ['.'])
        True
        >>> chat.run_tool_manually('nonexistent', [])
        'Unknown command: nonexistent'
        """
        function_to_call = AVAILABLE_FUNCTIONS.get(command)
        if function_to_call is None:
            return f'Unknown command: {command}'
        result = function_to_call(*args)
        output = str(result)
        self.messages.append(
            {
                "role": "user",
                "content": f"[Manual tool call] /{command} {' '.join(args)}\nOutput:\n{output}",
            }
        )
        return output


def completer(text, state):
    """
    Tab completion for slash commands and file paths.

    Returns the state-th completion option for the given text.
    >>> completer('', 0) is None
    True
    >>> completer('anything', 0) is None
    True
    >>> completer('something_else', 1) is None
    True
    """
    commands = list(AVAILABLE_FUNCTIONS.keys()) + ['compact']
    buffer = readline.get_line_buffer()

    if buffer.startswith('/'):
        parts = buffer[1:].split()
        if len(parts) == 0 or (len(parts) == 1 and not buffer.endswith(' ')):
            # Complete the command name
            matches = [f'/{c} ' for c in commands if c.startswith(text.lstrip('/'))]
        else:
            # Complete file paths
            matches = glob.glob(text + '*')
    else:
        matches = []

    try:
        return matches[state]
    except IndexError:
        return None


def repl(debug=False):
    """
    Run an interactive read-eval-print loop for the chat agent.
    Supports slash commands (e.g. /ls, /cat file.txt) for manual tool invocation.

    >>> def monkey_input(prompt, user_inputs=['/ls .']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl()
    chat> /ls .
    README.md
    __pycache__
    chat.py
    demo.gif
    pyproject.toml
    requirements.txt
    setup.cfg
    test_projects
    tools
    <BLANKLINE>
    """
    # Check for .git folder
    if not os.path.exists('.git'):
        print('Error: no .git folder found in current directory')
        return
    chat = Chat(debug=debug)
    readline.set_completer(completer)
    readline.parse_and_bind('tab: complete')
    try:
        while True:
            user_input = input("chat> ")
            if user_input.startswith("/"):
                parts = user_input[1:].split()
                command = parts[0] if parts else ""
                args = parts[1:]
                if command == "compact":
                    summary = compact(chat.messages)
                    chat.messages = [
                        {"role": "system", "content": f"Previous conversation summary: {summary}"}
                    ]
                    print(f"Compacted. Summary: {summary}")
                else:
                    output = chat.run_tool_manually(command, args)
                    print(output)
            else:
                response = chat.send_message(user_input, temperature=0)
                print(response)
    except (KeyboardInterrupt, EOFError):
        print()


def main():
    """
    Entry point that handles REPL mode, single message mode, and --debug flag.
    """
    import sys
    args = sys.argv[1:]
    debug = '--debug' in args
    args = [a for a in args if a != '--debug']

    if args:
        message = ' '.join(args)
        chat = Chat(debug=debug)
        print(chat.send_message(message, temperature=0))
    else:
        repl(debug=debug)


if __name__ == "__main__":
    main()
