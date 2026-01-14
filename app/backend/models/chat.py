from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime


class ChatMessage(BaseModel):
    """Individual chat message model."""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = None

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What is this document about?",
                "timestamp": "2026-01-14T10:30:00"
            }
        }


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    conversation_history: List[ChatMessage] = []
    use_rag: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Explain the main findings",
                "conversation_history": [],
                "use_rag": True
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint (non-streaming)."""
    response: str
    sources: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "response": "The main findings are...",
                "sources": ["document.pdf", "report.docx"]
            }
        }
