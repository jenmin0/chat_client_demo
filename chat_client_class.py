from openai import OpenAI
import json
from dotenv import load_dotenv
import os

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
        ...

    def save_history(self):
        """Save chat history in JSON form"""
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(self.messages, f, ensure_ascii=False)