from typing import List, Tuple
from app.backend.services.vector_store import VectorStore
from app.backend.services.embedding_service import generate_embedding


def build_augmented_prompt(
    query: str,
    context_chunks: List[Tuple[str, float, str]],
    conversation_history: List[dict] = None
) -> str:
    """
    Build an augmented prompt with retrieved context.

    Args:
        query: User's question
        context_chunks: List of (chunk_text, distance, filename) tuples from vector search
        conversation_history: Optional previous conversation messages

    Returns:
        Augmented prompt string
    """
    prompt_parts = []

    # System instruction
    prompt_parts.append(
        "You are a helpful AI assistant. Use the following context from uploaded documents "
        "to answer the user's question. If the context doesn't contain relevant information, "
        "you can provide a general answer but mention that it's not based on the uploaded documents."
    )

    # Add context if available
    if context_chunks:
        prompt_parts.append("\n\nContext from uploaded documents:")
        for i, (chunk, distance, filename) in enumerate(context_chunks, 1):
            prompt_parts.append(f"\n[Source: {filename}]")
            prompt_parts.append(f"{chunk}")

    # Add conversation history if available
    if conversation_history and len(conversation_history) > 0:
        prompt_parts.append("\n\nPrevious conversation:")
        for msg in conversation_history[-5:]:  # Last 5 messages to stay within limits
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"{role.capitalize()}: {content}")

    # Add user question
    prompt_parts.append(f"\n\nUser Question: {query}")
    prompt_parts.append("\nAnswer:")

    return "\n".join(prompt_parts)


async def get_relevant_context(
    query: str,
    vector_store: VectorStore,
    top_k: int = 5
) -> List[Tuple[str, float, str]]:
    """
    Retrieve relevant context for a query using RAG.

    Args:
        query: User's question
        vector_store: Vector store instance
        top_k: Number of relevant chunks to retrieve

    Returns:
        List of (chunk_text, distance, filename) tuples
    """
    # Check if vector store has data
    if vector_store.index.ntotal == 0:
        return []

    # Generate embedding for query
    query_embedding = await generate_embedding(query)

    # Search for similar chunks
    results = vector_store.search(query_embedding, k=top_k)

    return results
