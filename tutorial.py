import json
import os
from tools.calculate import calculate

from dotenv import 

from groq import Groq

# Initialize Groq client
client = Groq()
model = "openai/gpt-oss-120b"

def run_conversation(user_prompt):
    """Run a conversation with tool calling"""
    # Initialize the conversation
    messages = [
        {
            "role": "system",
            "content": "You are a calculator assistant. Use the calculate function to perform mathematical operations and provide the results."
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]


# Define tools
tools = [
    tool_schema
]
  
# Step 1: Make initial API call
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    # Step 2: Check if the model wants to call tools
    if tool_calls:
        # Map function names to implementations
        available_functions = {
            "calculate": calculate,
        }
        
        # Add the assistant's response to conversation
        messages.append(response_message)
        
        # Step 3: Execute each tool call
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                expression=function_args.get("expression")
            )
            
            # Add tool response to conversation
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })
        
        # Step 4: Get final response from model
        second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        return second_response.choices[0].message.content
    
    # If no tool calls, return the direct response
    return response_message.content

# Example usage
user_prompt = "What is 25 * 4 + 10?"
print(run_conversation(user_prompt))

