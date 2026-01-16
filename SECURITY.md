# Security Guide

This document outlines the security measures implemented in the RAG Chatbot and best practices for secure deployment.

## 🔒 Implemented Security Features

### 1. Rate Limiting

**Protection against**: API abuse, DDoS attacks, excessive Gemini API usage

- **Chat endpoints**: 10 requests per minute per IP
- **Upload endpoint**: 5 uploads per minute per IP
- **Implementation**: slowapi library with IP-based tracking

**Configuration** (in `app/middleware/settings/settings.py`):
```python
RATE_LIMIT_CHAT = "10/minute"
RATE_LIMIT_UPLOAD = "5/minute"
```

**What happens when limit exceeded**:
- HTTP 429 (Too Many Requests) response
- Automatic retry-after header included

### 2. Input Validation & Sanitization

**Protection against**: XSS, injection attacks, malicious input

**Implemented checks**:
- ✅ HTML/script tag removal using bleach library
- ✅ Null byte filtering
- ✅ Message length limits (4000 characters max)
- ✅ Conversation history truncation (20 messages max)

**Configuration**:
```python
MAX_MESSAGE_LENGTH = 4000
MAX_CONVERSATION_HISTORY = 20
ENABLE_SANITIZATION = True
```

### 3. File Upload Security

**Protection against**: Path traversal, malicious files, resource exhaustion

**Implemented checks**:
- ✅ Filename validation (no `../`, `/`, `\`, null bytes)
- ✅ File extension whitelist (.pdf, .txt, .docx only)
- ✅ File size limit (10MB default)
- ✅ Content extraction only (no execution)
- ✅ UUID-based storage (prevents overwrites)

**Configuration**:
```python
MAX_UPLOAD_SIZE_MB = 10
ALLOWED_FILE_TYPES = [".pdf", ".txt", ".docx"]
```

**Additional security layers to consider**:
- Antivirus scanning (integrate ClamAV for production)
- MIME type validation (not just extension)
- Sandboxed file processing

### 4. Security Headers

**Protection against**: Clickjacking, MIME sniffing, XSS, MITM attacks

**Implemented headers**:
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'
```

### 5. CORS Configuration

**Protection against**: Unauthorized cross-origin requests

**Configuration**: Whitelist only trusted origins
```python
CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
```

**For production**: Update to include your deployed URL
```python
CORS_ORIGINS = ["https://rag-chatbot-xxxx.onrender.com"]
```

### 6. Cost Protection & API Abuse Prevention ⭐ NEW

**Protection against**: API quota exhaustion, cost overruns, distributed attacks

This is the **most important security feature** for public deployment. Even with rate limiting, attackers can abuse your Gemini API by:
- Using multiple IPs (VPNs, proxies, botnets)
- Slowly draining quota over time
- Distributed attacks from multiple sources

**Implemented protections**:

#### Daily Quotas Per IP
- ✅ **Chat requests**: 100 per day per IP
- ✅ **File uploads**: 20 per day per IP
- ✅ **Token usage**: 10,000 tokens per day per IP (~10-20 conversations)
- ✅ Automatic reset at midnight UTC

**Configuration**:
```python
DAILY_CHAT_LIMIT_PER_IP = 100
DAILY_UPLOAD_LIMIT_PER_IP = 20
DAILY_TOKEN_LIMIT_PER_IP = 10000
```

#### Burst Detection
- ✅ **10-second window**: Max 5 requests
- ✅ **1-minute window**: Max 20 requests
- ✅ Automatic IP blocking on suspicious patterns

#### Token Cost Estimation
- ✅ Estimates tokens before making API call
- ✅ Blocks request if daily token limit would be exceeded
- ✅ Tracks both input and output tokens

**Check your usage**:
```bash
curl http://localhost:8000/api/usage
```

Response:
```json
{
  "client_ip": "203.0.113.42",
  "daily_chat_requests": 15,
  "daily_upload_requests": 3,
  "daily_tokens_used": 2450,
  "limits": {
    "chat_requests_per_day": 100,
    "upload_requests_per_day": 20,
    "tokens_per_day": 10000
  },
  "remaining": {
    "chat_requests": 85,
    "upload_requests": 17,
    "tokens": 7550
  }
}
```

**Error response when limit exceeded**:
```json
{
  "detail": "Daily limit exceeded. You can make 100 chat requests per day. Try again tomorrow.",
  "headers": {"Retry-After": "43200"}
}
```

**Cost calculation example**:

Gemini free tier: **1,000,000 tokens/day total**

With 10,000 tokens/day per IP:
- ✅ Supports ~100 concurrent users per day
- ✅ Each user can have ~10-20 conversations
- ✅ Protection against single user exhausting quota

**For production**:
1. Monitor actual usage patterns
2. Adjust limits based on traffic
3. Consider upgrading to Redis for distributed tracking:
```python
# Redis-based tracking (for multiple server instances)
import redis
r = redis.Redis(host='localhost', port=6379)
r.incr(f"daily:{ip}:{date}")
r.expire(f"daily:{ip}:{date}", 86400)
```

---

