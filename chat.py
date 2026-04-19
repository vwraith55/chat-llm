
import json
from groq import Groq
from dotenv import load_dotenv

from tools.calculate import calculate, calculate_tool_def
from tools.ls import ls, ls_tool_def
from tools.cat import cat, cat_tool_def
from tools.grep import grep, grep_tool_def

load_dotenv()

TOOLS = [calculate_tool_def, ls_tool_def, cat_tool_def, grep_tool_def]

AVAILABLE_FUNCTIONS = {
    "calculate": calculate,
    "ls": ls,
    "cat": cat,
    "grep": grep,
}


class Chat:
    """
    A conversational AI agent that maintains message history and supports tool use.

    The agent can call tools automatically when needed, or the user can invoke
    tools manually using slash commands (e.g. /ls, /cat, /grep).

    >>> chat = Chat()
    >>> result = chat.send_message('my name is bob. do not use any tools to answer this.',
    temperature=0.0)
    >>> 'bob' in result.lower()
    True
    >>> result2 = chat.send_message('what is my name? do not use any tools to answer this.',
    temperature=0.0)
    >>> 'bob' in result2.lower()
    True
    >>> chat2 = Chat()
    >>> result3 = chat2.send_message('what is my name? do not use any tools to answer this.',
    temperature=0.0)
    >>> 'bob' in result3.lower()
    False
    """

    client = Groq()

    def __init__(self):
        self.MODEL = "llama-3.1-8b-instant"
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

        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            model=self.MODEL,
            temperature=temperature,
            seed=0,
            tools=TOOLS,
            tool_choice="auto",
        )

        response_message = chat_completion.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            # Add assistant's tool-use message to history
            self.messages.append(response_message)

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
        >>> output = chat.run_tool_manually('ls', ['.'])
        >>> isinstance(output, str)
        True
        >>> chat.run_tool_manually('nonexistent', [])
        'Unknown command: nonexistent'
        """
        function_to_call = AVAILABLE_FUNCTIONS.get(command)

        if function_to_call is None:
            return f'Unknown command: {command}'

        result = function_to_call(*args)
        output = str(result)

        # Add to history so LLM has context
        self.messages.append(
            {
                "role": "user",
                "content": f"[Manual tool call] /{command} {' '.join(args)}\nOutput:\n{output}",
            }
        )
        return output


def repl():
    """
    Run an interactive read-eval-print loop for the chat agent.

    Supports slash commands (e.g. /ls, /cat file.txt) for manual tool invocation.

    >>> def monkey_input(prompt, user_inputs=['Hello!', '/ls .', 'Goodbye.']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl()  # doctest: +ELLIPSIS
    chat> Hello!
    ...
    chat> /ls .
    ...
    chat> Goodbye.
    ...
    <BLANKLINE>
    """
    chat = Chat()
    try:
        while True:
            user_input = input("chat> ")

            if user_input.startswith("/"):
                parts = user_input[1:].split()
                command = parts[0] if parts else ""
                args = parts[1:]
                output = chat.run_tool_manually(command, args)
                print(output)
            else:
                response = chat.send_message(user_input, temperature=0)
                print(response)

    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == "__main__":
    repl()
