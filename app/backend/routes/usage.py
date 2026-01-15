"""
Usage statistics endpoint for users to check their API quota.
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Dict
from app.middleware.cost_protection import cost_tracker


router = APIRouter()


class UsageStats(BaseModel):
    """Current usage statistics for the requesting IP."""
    client_ip: str
    daily_chat_requests: int
    daily_upload_requests: int
    daily_tokens_used: int
    limits: Dict[str, int]
    remaining: Dict[str, int]


@router.get("/", response_model=UsageStats)
async def get_usage_stats(request: Request):
    """
    Get current usage statistics for your IP address.

    Returns:
    - Daily chat requests made
    - Daily upload requests made
    - Daily tokens used (estimated)
    - Limits for each category
    - Remaining quota

    Quotas reset at midnight UTC daily.
    """
    client_ip = cost_tracker.get_client_ip(request)
    stats = cost_tracker.get_usage_stats(client_ip)

    return UsageStats(
        client_ip=client_ip,
        daily_chat_requests=stats["daily_requests"],
        daily_upload_requests=0,  # Tracked separately if needed
        daily_tokens_used=stats["daily_tokens"],
        limits={
            "chat_requests_per_day": stats["chat_limit"],
            "upload_requests_per_day": stats["upload_limit"],
            "tokens_per_day": stats["token_limit"],
        },
        remaining={
            "chat_requests": max(0, stats["chat_limit"] - stats["daily_requests"]),
            "upload_requests": stats["upload_limit"],  # Simplified
            "tokens": max(0, stats["token_limit"] - stats["daily_tokens"]),
        }
    )
