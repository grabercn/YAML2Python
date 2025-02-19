# chatgpt_client.py
from openai import OpenAI
import os
import tiktoken

class ChatGPTClient:
    MAX_CONTEXT_TOKENS = 8192  # Maximum tokens allowed in the model's context
    CONTEXT_MARGIN = 10        # Extra tokens reserved to avoid overshooting the limit
    MESSAGE_OVERHEAD = 3       # Estimated overhead per message (for role markers and formatting)

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

    def count_tokens(self, text: str, model: str) -> int:
        """
        Uses tiktoken to count tokens for a given text according to the specified model.
        """
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))

    def get_response(
        self,
        prompt_text: str = "Return: PROMPT NOT PROVIDED: PLEASE CHECK YOUR INPUT PARAMETERS",
        model: str = "gpt-4",
        max_tokens: int = 8000,  # user-requested maximum tokens for the response
        system_prompt: str = "Return: PROMPT NOT PROVIDED: PLEASE CHECK YOUR INPUT PARAMETERS"
    ) -> str:
        """
        Sends a chat completion request to the ChatGPT API, ensuring that the total token count
        (input tokens plus response tokens) does not exceed the model's maximum context.

        Parameters:
        - prompt_text: The text prompt for the user message.
        - model: The model to use (default: "gpt-4").
        - max_tokens: The maximum number of tokens for the response.
        - system_prompt: The system prompt that defines assistant behavior.

        Returns:
        - The text response from the assistant.
        """
        # Count tokens for system and user messages using tiktoken.
        system_tokens = self.count_tokens(system_prompt, model)
        user_tokens = self.count_tokens(prompt_text, model)
        # Add overhead for each message (system and user).
        total_input_tokens = system_tokens + user_tokens + 2 * self.MESSAGE_OVERHEAD

        # Check if the input itself is already too large.
        if total_input_tokens >= self.MAX_CONTEXT_TOKENS:
            raise ValueError("The provided input messages exceed the maximum allowed context length.")

        # Calculate available tokens for the completion, subtracting the safety margin.
        available_response_tokens = self.MAX_CONTEXT_TOKENS - total_input_tokens - self.CONTEXT_MARGIN
        allowed_response_tokens = min(max_tokens, available_response_tokens)

        if allowed_response_tokens < 1:
            raise ValueError("Not enough tokens left for the response. Please shorten your input.")

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=allowed_response_tokens
        )
        return response.choices[0].message.content.strip()

# This block allows for testing the module directly.
if __name__ == "__main__":
    test_prompt = "Hello!"
    chat_client = ChatGPTClient()
    print(chat_client.get_response(test_prompt))
