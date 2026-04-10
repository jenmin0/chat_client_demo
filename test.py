from unittest.mock import MagicMock, patch
from chat_client_class import *

def test_chat_returns_answer():
    client = OpenAIClient(model="gpt-4o")
    
    # Build a mock response object
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello!"
    
    # Use patch to replace the real API call
    with patch.object(client.client.chat.completions, "create", return_value=mock_response):
        answer = client.chat("Hi")
        assert answer == "Hello!"

def test_chat_with_history_returns_answer():
    client = OpenAIClient(model="gpt-4o", temperature=1, max_tokens=10)
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "I'm fine, thank you!"

    with patch.object(client.client.chat.completions,"create",return_value=mock_response):
        answer = client.chat_with_history("How are you?")
        assert answer == "I'm fine, thank you!"
        assert client.messages[0]["role"] == "user"
        assert client.messages[1]["role"] == "assistant"

def test_reset_history_clears_messages():
    client = OpenAIClient(model="gpt-4o")
    client.messages = [{"role": "user", "content": "Hello!"}]
    client.reset_history()
    assert client.messages == []

def test_system_prompt_is_set():
    client = OpenAIClient(model="gpt-4o")
    client.set_system_prompt("You are a professor of computer science.")
    with patch.object(client.client.chat.completions,"create",return_value=MagicMock(choices=[MagicMock(message=MagicMock(content="Hello!"))])):
        answer = client.chat_with_history("Good Morning, professor!")
        assert client.prompt == {"role": "system", "content": "You are a professor of computer science."}
        assert client.messages[0]["role"] == "user"
        assert client.messages[1]["role"] == "assistant"
        # assert answer == "Hello!"


def test_chat_with_tools_calls_tool():
    client = OpenAIClient(model="gpt-4o")
    client.register_tool(get_weather, "A tool to get weather information.", 
                         {"type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city for which to get weather information."
                            }
                        },
                    "required": ["city"]
                                        })
    
    mock_response = MagicMock()
    # First Respond
    first_response = MagicMock()
    # Tools call in the first response
    tool_call = MagicMock()
    tool_call.id = "call_123"
    tool_call.function.name = "get_weather"
    tool_call.function.arguments = json.dumps({"city": "New York"})
    first_response.choices[0].message.tool_calls = [tool_call]
    first_response.choices[0].message.content = None

    # Second Respond
    second_response = MagicMock()
    second_response.choices[0].message.tool_calls = None
    second_response.choices[0].message.content = "New York today is sunny with a high of 25°C."

    with patch.object(
        client.client.chat.completions,
        "create",
        side_effect=[first_response, second_response]
    ):
        answer = client.chat_with_tools("What's the weather in New York?")
        assert answer == "New York today is sunny with a high of 25°C."

def test_chat_with_tools_integration():
    client = OpenAIClient(model="gpt-4o")
    client.register_tool(get_weather, "Get weather for a city.", {"type": "object",
                                            "properties": {
                                                "city": {
                                                    "type": "string",
                                                    "description": "The city for which to get weather information."
                                                }
                                            },
                                        "required": ["city"]
                                        })
    client.register_tool(calculate, "Calculate a math expression.", {"type": "object",
                                            "properties": {
                                                "expression": {
                                                    "type": "string",
                                                    "description": "The math expression to calculate."
                                                }
                                            },
                                        "required": ["expression"]
                                        })

    answer = client.chat_with_tools("How's the weather in Frankfurt and what is 123 * 456?")
    # print("Final Answer: ", answer)
    assert answer is not None
    assert isinstance(answer, str)
    assert len(answer) > 0
    assert "56,088" in answer  