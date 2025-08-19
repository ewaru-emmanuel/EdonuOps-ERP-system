# backend/modules/ai/copilot.py

import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_copilot(prompt):
    """
    Sends a prompt to the OpenAI API and returns the generated response.
    This is a placeholder and requires a valid OpenAI API key.
    """
    if not openai.api_key:
        return "Error: OpenAI API key is not set. Please configure your environment variables."

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"An error occurred: {e}"