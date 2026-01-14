from typing import List
from google import genai
from app.middleware.settings.settings import config


# Initialize Gemini client
client = genai.Client(api_key=config.GEMINI_API_KEY.get_secret_value())


async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text using Gemini Embedding API.

    Args:
        text: Text to embed

    Returns:
        List of floats representing the embedding vector
    """
    if not text.strip():
        raise ValueError("Text cannot be empty")

    try:
        result = await client.aio.models.embed_content(
            model=config.GEMINI_EMBEDDING_MODEL,
            content=text
        )
        return result.embeddings[0].values
    except Exception as e:
        raise Exception(f"Error generating embedding: {str(e)}")


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts efficiently.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    if not texts:
        return []

    embeddings = []
    for text in texts:
        if text.strip():
            try:
                embedding = await generate_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                print(f"Warning: Failed to generate embedding for text: {str(e)}")
                # Append a zero vector as fallback
                embeddings.append([0.0] * config.EMBEDDING_DIMENSION)
        else:
            # Empty text gets zero vector
            embeddings.append([0.0] * config.EMBEDDING_DIMENSION)

    return embeddings
