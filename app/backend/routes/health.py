from fastapi import APIRouter
from app.backend.services.vector_store import vector_store

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    stats = vector_store.get_stats()
    return {
        "status": "healthy",
        "service": "rag-chatbot",
        "vector_store": stats
    }
