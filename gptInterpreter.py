# chatgpt_client.py
from openai import OpenAI
import os

class ChatGPTClient:
    def __init__(self, api_key: str = None):
        """
        Initializes the ChatGPTClient with an API key.
        If no API key is provided, it attempts to retrieve it from the
        environment variable 'OPENAI_API_KEY'.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set as environment variable 'OPENAI_API_KEY'")
        self.client = OpenAI(api_key=self.api_key)

    def get_response(
        self,
        prompt_text: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 150,
        system_prompt: str = """You are a programming language interpreter that outputs and yaml code given into python code that is then executed by the machine.
                                If the yaml given is wrong syntax say that, act exactly like a compiler / interpreter and say so, and do not return any python code but an error in the format
                                Status: (status - syntax is good, not good, and the error line)
                                Code: (syntactically correct code here that i will parse (python) to be executed)"""
    ) -> str:
        """
        Sends a chat completion request to the ChatGPT API.

        Parameters:
        - prompt_text: The text prompt for the user message.
        - model: The model to use (default: "gpt-3.5-turbo").
        - max_tokens: The maximum number of tokens in the response.
        - system_prompt: The system prompt that defines assistant behavior.

        Returns:
        - The text response from the assistant.
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()

# This block allows for testing the module directly.
if __name__ == "__main__":
    test_prompt = "Hello!"
    chat_client = ChatGPTClient()
    print(chat_client.get_response(test_prompt))
