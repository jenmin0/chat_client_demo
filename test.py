from unittest.mock import MagicMock, patch
from chat_client_class import OpenAIClient

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

