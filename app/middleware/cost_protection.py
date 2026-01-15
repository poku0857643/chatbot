"""
Cost protection middleware for Gemini API usage.

Prevents API abuse and cost overruns by:
- Tracking daily requests per IP
- Estimating token usage and costs
- Detecting suspicious activity patterns
- Enforcing daily quotas
"""
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple
import time
from fastapi import HTTPException, Request
from app.middleware.settings.settings import config


class CostProtectionTracker:
    """
    In-memory tracker for API usage and cost protection.

    For production with multiple instances, migrate to Redis:
    - redis.incr(f"daily:{ip}:{date}")
    - redis.expire(f"daily:{ip}:{date}", 86400)
    """

    def __init__(self):
        # Daily request count per IP: {ip: {date: count}}
        self.daily_requests: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        # Request timestamps per IP (for burst detection): {ip: [timestamp1, timestamp2, ...]}
        self.request_history: Dict[str, list] = defaultdict(list)

        # Token usage estimation per IP: {ip: {date: token_count}}
        self.daily_tokens: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        # Last cleanup time
        self.last_cleanup = time.time()

    def cleanup_old_data(self):
        """Remove data older than 2 days to prevent memory bloat."""
        current_time = time.time()

        # Cleanup every hour
        if current_time - self.last_cleanup < 3600:
            return

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        cutoff_date_str = yesterday.isoformat()

        # Clean daily requests
        for ip in list(self.daily_requests.keys()):
            old_dates = [date for date in self.daily_requests[ip] if date < cutoff_date_str]
            for date in old_dates:
                del self.daily_requests[ip][date]
            if not self.daily_requests[ip]:
                del self.daily_requests[ip]

        # Clean daily tokens
        for ip in list(self.daily_tokens.keys()):
            old_dates = [date for date in self.daily_tokens[ip] if date < cutoff_date_str]
            for date in old_dates:
                del self.daily_tokens[ip][date]
            if not self.daily_tokens[ip]:
                del self.daily_tokens[ip]

        # Clean request history (keep only last 10 minutes)
        cutoff_time = current_time - 600
        for ip in list(self.request_history.keys()):
            self.request_history[ip] = [
                ts for ts in self.request_history[ip] if ts > cutoff_time
            ]
            if not self.request_history[ip]:
                del self.request_history[ip]

        self.last_cleanup = current_time

    def get_client_ip(self, request: Request) -> str:
        """
        Get client IP address, handling proxies and load balancers.

        Render.com sets X-Forwarded-For header.
        """
        # Check for proxy headers (Render, Cloudflare, etc.)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can be: "client, proxy1, proxy2"
            return forwarded_for.split(",")[0].strip()

        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Rule of thumb: 1 token ≈ 4 characters for English text.
        This is conservative; actual count may be lower.
        """
        return len(text) // 4 + 1

    def check_daily_limit(self, ip: str, endpoint: str) -> None:
        """
        Check if IP has exceeded daily quota.

        Raises HTTPException 429 if limit exceeded.
        """
        self.cleanup_old_data()

        today = datetime.now().date().isoformat()
        current_requests = self.daily_requests[ip][today]

        # Different limits for different endpoints
        if endpoint == "chat":
            daily_limit = config.DAILY_CHAT_LIMIT_PER_IP
        elif endpoint == "upload":
            daily_limit = config.DAILY_UPLOAD_LIMIT_PER_IP
        else:
            daily_limit = 100  # Default

        if current_requests >= daily_limit:
            raise HTTPException(
                status_code=429,
                detail=f"Daily limit exceeded. You can make {daily_limit} {endpoint} requests per day. Try again tomorrow.",
                headers={"Retry-After": str(self._seconds_until_midnight())}
            )

    def check_burst_activity(self, ip: str) -> None:
        """
        Detect and block burst/bot activity.

        Flags suspicious if:
        - More than 5 requests in 10 seconds
        - More than 20 requests in 1 minute
        """
        current_time = time.time()

        # Add current request
        self.request_history[ip].append(current_time)

        # Count recent requests
        last_10s = sum(1 for ts in self.request_history[ip] if ts > current_time - 10)
        last_60s = sum(1 for ts in self.request_history[ip] if ts > current_time - 60)

        if last_10s > 5:
            raise HTTPException(
                status_code=429,
                detail="Too many requests in short time. Please slow down.",
                headers={"Retry-After": "10"}
            )

        if last_60s > 20:
            raise HTTPException(
                status_code=429,
                detail="Suspicious activity detected. Please wait before trying again.",
                headers={"Retry-After": "60"}
            )

    def check_token_limit(self, ip: str, estimated_tokens: int) -> None:
        """
        Check if IP has exceeded daily token quota.

        Gemini free tier: 1M tokens/day total
        Per-IP limit: Conservative to allow ~100 users/day
        """
        today = datetime.now().date().isoformat()
        current_tokens = self.daily_tokens[ip][today]

        daily_token_limit = config.DAILY_TOKEN_LIMIT_PER_IP

        if current_tokens + estimated_tokens > daily_token_limit:
            raise HTTPException(
                status_code=429,
                detail=f"Daily token limit exceeded ({daily_token_limit:,} tokens/day per user). Try again tomorrow.",
                headers={"Retry-After": str(self._seconds_until_midnight())}
            )

    def record_request(self, ip: str, endpoint: str, estimated_tokens: int = 0) -> None:
        """
        Record a successful request for tracking.
        """
        today = datetime.now().date().isoformat()
        self.daily_requests[ip][today] += 1

        if estimated_tokens > 0:
            self.daily_tokens[ip][today] += estimated_tokens

    def get_usage_stats(self, ip: str) -> Dict[str, int]:
        """
        Get current usage statistics for an IP.
        """
        today = datetime.now().date().isoformat()
        return {
            "daily_requests": self.daily_requests[ip][today],
            "daily_tokens": self.daily_tokens[ip][today],
            "chat_limit": config.DAILY_CHAT_LIMIT_PER_IP,
            "upload_limit": config.DAILY_UPLOAD_LIMIT_PER_IP,
            "token_limit": config.DAILY_TOKEN_LIMIT_PER_IP,
        }

    def _seconds_until_midnight(self) -> int:
        """Calculate seconds until midnight UTC."""
        now = datetime.now()
        midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        return int((midnight - now).total_seconds())


# Global singleton instance
cost_tracker = CostProtectionTracker()


async def check_cost_limits(
    request: Request,
    endpoint: str,
    message: str = None
) -> str:
    """
    Middleware function to check cost limits before processing request.

    Args:
        request: FastAPI request object
        endpoint: "chat" or "upload"
        message: Optional message text for token estimation

    Returns:
        Client IP address

    Raises:
        HTTPException 429 if limits exceeded
    """
    ip = cost_tracker.get_client_ip(request)

    # Check burst activity (bot detection)
    cost_tracker.check_burst_activity(ip)

    # Check daily request limit
    cost_tracker.check_daily_limit(ip, endpoint)

    # Estimate and check token limit (for chat)
    if message and endpoint == "chat":
        estimated_tokens = cost_tracker.estimate_tokens(message)
        cost_tracker.check_token_limit(ip, estimated_tokens)

    return ip


def record_usage(ip: str, endpoint: str, tokens: int = 0):
    """
    Record usage after successful request.
    """
    cost_tracker.record_request(ip, endpoint, tokens)
