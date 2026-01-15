from google import genai
from app.middleware.settings.settings import config
from typing import AsyncIterator


# Initialize Gemini client (singleton)
client = genai.Client(api_key=config.GEMINI_API_KEY.get_secret_value())


def generate_content_stream(prompt: str) -> AsyncIterator[str]:
    """
    Generate content with streaming support.

    Args:
        prompt: The prompt to send to the model

    Yields:
        Text chunks as they are generated
    """
    response = client.models.generate_content_stream(
        model=config.GEMINI_MODEL,
        contents=prompt
    )

    for chunk in response:
        if chunk.text:
            yield chunk.text


async def generate_content_async(prompt: str) -> str:
    """
    Generate content asynchronously (non-streaming).

    Args:
        prompt: The prompt to send to the model

    Returns:
        Complete generated text
    """
    response = await client.aio.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt
    )

    return response.text




