"""
Security utilities for input validation and sanitization.
"""
import bleach
import re
from typing import Optional
from app.middleware.settings.settings import config


def sanitize_text(text: str) -> str:
    """
    Sanitize user input by removing potentially dangerous HTML/scripts.

    Args:
        text: User input text

    Returns:
        Sanitized text safe for processing
    """
    if not config.ENABLE_SANITIZATION:
        return text

    # Remove HTML tags and scripts
    cleaned = bleach.clean(text, tags=[], strip=True)

    # Remove null bytes
    cleaned = cleaned.replace('\x00', '')

    return cleaned


def validate_filename(filename: str) -> bool:
    """
    Validate filename to prevent path traversal attacks.

    Args:
        filename: Uploaded filename

    Returns:
        True if filename is safe, False otherwise
    """
    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False

    # Check for null bytes
    if '\x00' in filename:
        return False

    # Check filename length
    if len(filename) > 255:
        return False

    # Ensure filename has valid characters only
    valid_pattern = re.compile(r'^[\w\-. ]+$')
    return bool(valid_pattern.match(filename))


def validate_message_length(message: str, max_length: Optional[int] = None) -> bool:
    """
    Validate message length to prevent abuse.

    Args:
        message: User message
        max_length: Maximum allowed length (defaults to config)

    Returns:
        True if message length is valid
    """
    max_len = max_length or config.MAX_MESSAGE_LENGTH
    return len(message) <= max_len


def truncate_conversation_history(history: list, max_messages: Optional[int] = None) -> list:
    """
    Truncate conversation history to prevent memory abuse.

    Args:
        history: Conversation history
        max_messages: Maximum messages to keep (defaults to config)

    Returns:
        Truncated history
    """
    max_msgs = max_messages or config.MAX_CONVERSATION_HISTORY
    if len(history) > max_msgs:
        return history[-max_msgs:]
    return history
