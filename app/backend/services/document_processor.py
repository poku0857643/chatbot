from fastapi import UploadFile, HTTPException
from pathlib import Path
from typing import List
import PyPDF2
import docx
import aiofiles
from app.middleware.settings.settings import config


async def process_uploaded_file(file: UploadFile) -> List[str]:
    """
    Extract text from uploaded file and split into chunks.

    Args:
        file: UploadFile object from FastAPI

    Returns:
        List of text chunks

    Raises:
        HTTPException: If file type is unsupported or processing fails
    """
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in config.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not supported. Allowed types: {', '.join(config.ALLOWED_FILE_TYPES)}"
        )

    # Read file content
    content = await file.read()

    # Extract text based on file type
    try:
        if file_extension == ".pdf":
            text = extract_text_from_pdf(content)
        elif file_extension == ".txt":
            text = content.decode('utf-8')
        elif file_extension == ".docx":
            text = extract_text_from_docx(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    # Chunk the text
    chunks = chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)

    return chunks


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF file bytes."""
    from io import BytesIO

    pdf_file = BytesIO(content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"

    return text.strip()


def extract_text_from_docx(content: bytes) -> str:
    """Extract text from DOCX file bytes."""
    from io import BytesIO

    docx_file = BytesIO(content)
    doc = docx.Document(docx_file)

    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"

    return text.strip()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: The full text to chunk
        chunk_size: Target size of each chunk (in words)
        overlap: Number of words to overlap between chunks

    Returns:
        List of text chunks
    """
    if not text.strip():
        return []

    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)

        # Stop if we've reached the end
        if i + chunk_size >= len(words):
            break

    return chunks


async def save_uploaded_file(file: UploadFile, file_id: str) -> Path:
    """
    Save uploaded file to disk.

    Args:
        file: UploadFile object
        file_id: Unique identifier for the file

    Returns:
        Path to saved file
    """
    # Reset file pointer
    await file.seek(0)

    # Create upload directory if it doesn't exist
    upload_dir = Path(config.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate file path
    file_extension = Path(file.filename).suffix
    file_path = upload_dir / f"{file_id}{file_extension}"

    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    return file_path
