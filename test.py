from unittest.mock import MagicMock, patch
from client import *
from tools import get_weather, calculate, get_account_info, get_transactions, calculate_summary

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
    client.register_tool(get_account_info,"Get account information by account_id.", {"type":"object",
                                            "properties":{
                                                "account_id": {
                                                    "type": "string",
                                                    "description": "The account id to get information for."
                                                }
                                            },
                                            "required": ["account_id"]})
    client.register_tool(get_transactions,"Get the last n transactions for account_id.", {"type":"object",
                                        "properties": {
                                            "account_id": {
                                                "type": "string",
                                                "description": "The account id for which to get transactions."
                                            },
                                            "n": {
                                                "type": "integer",
                                                "description": "The number of transactions to retrieve."
                                            }
                                        },
                                    "required": ["account_id"]
                                    })
    client.register_tool(calculate_summary,"Calculate the total in, total out and net for the last n transactions.", {"type":"object",
                                        "properties": {
                                            "account_id": {
                                                "type": "string",
                                                "description": "The account id for which to calculate summary."
                                            },
                                            "n": {
                                                "type": "integer",
                                                "description": "The number of transactions to include in the summary."
                                            }
                                        },
                                    "required": ["account_id"]
                                    })

    answer = client.chat_with_tools("How's the weather in Frankfurt and what is 123 * 456? Also, give me the account info, last 5 transactions and summary for account A001 and calculate the net for the transactions.")
    assert answer is not None
    assert isinstance(answer, str)
    # assert len(answer) > 0
    # assert "56,088" in answer

def test_chat_with_tools_and_history():
    client = OpenAIClient(model="gpt-4o")
    client.prompt = {"role": "system", "content": "Don't make assumptions about what "
        "values to plug into functions. Don't make up values to fill the response with. "
        "Ask for clarification if needed."}
    client.register_tool(get_account_info,"Get account information by account_id.", {"type":"object",
                                            "properties":{
                                                "account_id": {
                                                    "type": "string",
                                                    "description": "The account id to get information for."
                                                }
                                            },
                                            "required": ["account_id"]})
    client.register_tool(get_transactions,"Get the last n transactions for account_id.", {"type":"object",
                                        "properties": {
                                            "account_id": {
                                                "type": "string",
                                                "description": "The account id for which to get transactions."
                                            },
                                            "n": {
                                                "type": "integer",
                                                "description": "The number of transactions to retrieve."
                                            }
                                        },
                                    "required": ["account_id"]
                                    })
    client.register_tool(calculate_summary,"Calculate the total in, total out and net for the last n transactions.", {"type":"object",
                                        "properties": {
                                            "account_id": {
                                                "type": "string",
                                                "description": "The account id for which to calculate summary."
                                            },
                                            "n": {
                                                "type": "integer",
                                                "description": "The number of transactions to include in the summary."
                                            }
                                        },
                                    "required": ["account_id"]
                                    })
    client.chat_with_tools_and_history("Give me the account info for A001.")
    client.chat_with_tools_and_history("Now show me the last 3 transactions for that account.")
    client.chat_with_tools_and_history("And what's the summary for those transactions?")

