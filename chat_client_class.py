from openai import OpenAI
import json
from dotenv import load_dotenv
import os
import tiktoken

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class OpenAIClient:
    def __init__(self, model, temperature = 0, max_tokens = 50):
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.max_tokens = max_tokens
        self.messages = []
        self.prompt = ""
        self.tools = []

    def chat(self, text):
        """Single chat, the chat history is not taken into account"""
        temp_messages = ([self.prompt] if self.prompt else []) + [{"role":"user","content":text}]
        print("User: ", text)
        response = self.client.chat.completions.create(
            model = self.model,
            messages = temp_messages,
            max_completion_tokens = self.max_tokens,
            temperature = self.temperature
        )
        answer = response.choices[0].message.content
        print("Assistant: ", answer)
        return answer

    def chat_with_history(self, text):
        """Start a new chat based on chat history"""
        self.messages.append({"role":"user","content":text})
        print("User: ", text)
        response = self.client.chat.completions.create(
            model = self.model,
            messages = ([self.prompt] if self.prompt else []) + self.messages,
            max_completion_tokens = self.max_tokens,
            temperature = self.temperature
        )
        answer = response.choices[0].message.content
        print("Assistant: ", answer)
        self.messages.append({"role":"assistant","content":answer})
        return answer

    def reset_history(self):
        """Remove chat history"""
        self.messages = []

    def set_system_prompt(self, prompt):
        """Prepare a system prompt for coming chat."""
        self.prompt = {"role":"system","content":prompt}
        

    def count_tokens(self, text):
        """Count input tokens. """
        encoding = tiktoken.encoding_for_model(self.model)
        return len(encoding.encode(text))

    def save_history(self):
        """Save chat history in JSON form"""
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(self.messages, f, ensure_ascii=False)

    def register_tool(self,function, description, parameters):
        """Register a tool for the agent."""
        self.tools.append({"type":"function", 
                           "function": {"name": function.__name__, "description": description, 
                                        "parameters": parameters
                                        }
                           })
                           
        
    def chat_with_tools(self, text):
        """Start a new chat with tools."""

        temp_messages = [{"role": "system", "content": "Don't make assumptions about what "
        "values to plug into functions. Don't make up values to fill the response with. "
        "Ask for clarification if needed."},
        {"role":"user","content":text}]

        print("User: ", text)
        response = self.client.chat.completions.create(
            model = self.model,
            messages = temp_messages,
            tools = self.tools
        )

        message = response.choices[0].message
        if message.tool_calls:
            temp_messages.append(message)
            for call in message.tool_calls:
                tool_name = call.function.name
                arguments = json.loads(call.function.arguments)
                tool_result = self._execute_tool(tool_name, arguments)
                print(f"Tool {tool_name} called with arguments {arguments}, returned {tool_result}")
                temp_messages.append({"role":"tool","tool_call_id": call.id,"content": tool_result})

            second_response = self.client.chat.completions.create(
                model = self.model,
                messages = temp_messages,
                tools=self.tools
            )

            answer = second_response.choices[0].message.content
        else:
            answer = message.content
        print("Assistant: ", answer)
        return answer
    
    def _execute_tool(self, tool_name, arguments):
        """Execute the tool and return the result."""
        if tool_name == "get_weather":
            return get_weather(**arguments)
        elif tool_name == "calculate":
            return calculate(**arguments)
        else:
            return f"Tool {tool_name} not found."

    

def get_weather(city):
    """Example tool function to get weather information."""
    return f"{city} today is sunny with a high of 25°C and a low of 15°C."

def calculate(expression):
    return str(eval(expression))

