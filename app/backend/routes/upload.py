from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
from app.backend.models.upload import FileUploadResponse
from app.backend.services.document_processor import process_uploaded_file, save_uploaded_file
from app.backend.services.embedding_service import generate_embeddings_batch
from app.backend.services.vector_store import vector_store
from app.middleware.settings.settings import config

router = APIRouter()


@router.post("/", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a document for RAG.

    Supports: PDF, TXT, DOCX files (max 10MB)
    """
    # Validate file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in config.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not supported. Allowed types: {', '.join(config.ALLOWED_FILE_TYPES)}"
        )

    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()  # Get position (file size)
    file.file.seek(0)  # Reset to beginning

    max_size = config.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convert to bytes
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size ({config.MAX_UPLOAD_SIZE_MB}MB)"
        )

    try:
        # Generate unique file ID
        file_id = str(uuid.uuid4())

        # Process file to extract and chunk text
        chunks = await process_uploaded_file(file)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the file"
            )

        # Generate embeddings for chunks
        embeddings = await generate_embeddings_batch(chunks)

        # Add to vector store
        chunks_added = vector_store.add_documents(
            embeddings=embeddings,
            chunks=chunks,
            file_id=file_id,
            filename=file.filename
        )

        # Save file to disk
        await save_uploaded_file(file, file_id)

        return FileUploadResponse(
            filename=file.filename,
            file_id=file_id,
            chunks_created=chunks_added,
            status="success",
            message=f"File processed successfully. {chunks_added} chunks indexed."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )
