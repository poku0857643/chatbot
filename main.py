from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.middleware.settings.settings import config
from app.backend.routes import chat, upload, health


app = FastAPI(
    title="RAG Chatbot API",
    description="A chatbot with Retrieval Augmented Generation capabilities",
    version="1.0.0"
)

# CORS middleware for React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

# Serve static files (production React build)
# This should be LAST to not override API routes
frontend_dist = Path("app/frontend/dist")
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")




