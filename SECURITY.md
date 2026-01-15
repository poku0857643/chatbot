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

## 🔑 API Key Security Best Practices

### ⚠️ CRITICAL: Protect Your GEMINI_API_KEY

Your Gemini API key (`AIzaSyD3Vr70iolk-cOmdMRBwzAov9kxjadhaH4`) is like a password. If exposed publicly, attackers can:
- Use your free tier quota
- Generate large API bills (if you upgrade)
- Access your Google AI resources

### ✅ DO:

1. **Never commit API keys to Git**
   - ✅ Already protected by `.gitignore` (.env file excluded)
   - ✅ Verify: `git status` should NOT show `.env`

2. **Use environment variables on Render**
   - ✅ Add `GEMINI_API_KEY` as environment variable in Render dashboard
   - ✅ Never paste API key in code or public config files

3. **Rotate API keys regularly**
   - Go to https://aistudio.google.com/app/apikey
   - Create new API key
   - Update environment variable on Render
   - Delete old key

4. **Monitor API usage**
   - Check Google AI Studio dashboard regularly
   - Set up usage alerts if available
   - Watch for unexpected spikes

5. **Use different keys for dev/prod**
   - Development: One API key for local testing
   - Production: Separate API key for deployed app
   - Easy to revoke if compromised

### ❌ DON'T:

1. ❌ Never hardcode API keys in source code
2. ❌ Never share API keys in screenshots, videos, or demos
3. ❌ Never commit `.env` file to GitHub
4. ❌ Never expose API keys in client-side code
5. ❌ Never share API keys via email, Slack, or chat

### 🔄 API Key Rotation (Recommended Every 90 Days)

**Step-by-step process**:

1. **Create new API key** at https://aistudio.google.com/app/apikey
   - Click "Create API Key"
   - Copy the new key

2. **Update local .env file**:
   ```bash
   # .env
   GEMINI_API_KEY=your_new_api_key_here
   ```

3. **Update Render environment variable**:
   - Go to Render dashboard → Your service
   - Click "Environment" tab
   - Edit `GEMINI_API_KEY` variable
   - Paste new key
   - Click "Save Changes" (auto-redeploys)

4. **Test deployment**:
   - Visit your deployed URL
   - Upload a test document
   - Send a test message
   - Verify it works

5. **Delete old API key** at https://aistudio.google.com/app/apikey
   - Ensures old key can't be used if compromised

### 🚨 If Your API Key Is Compromised

**Immediate actions**:

1. **Delete compromised key ASAP**
   - Go to https://aistudio.google.com/app/apikey
   - Click delete on the compromised key

2. **Create new key and update**
   - Follow rotation steps above

3. **Check usage logs**
   - Review API usage for suspicious activity
   - Check if quota was exceeded

4. **Update all deployments**
   - Update Render environment variable
   - Update local `.env` file
   - Update any other environments

---

## 📊 Monitoring & Cost Control

### Real-Time Usage Monitoring

**Check usage via API**:
```bash
# Your current usage
curl https://your-app.onrender.com/api/usage

# Example response
{
  "daily_chat_requests": 42,
  "daily_tokens_used": 5230,
  "remaining": {
    "chat_requests": 58,
    "tokens": 4770
  }
}
```

**Add usage display to your frontend** (optional):
```javascript
// In React component
const [usage, setUsage] = useState(null);

useEffect(() => {
  fetch('/api/usage')
    .then(res => res.json())
    .then(data => setUsage(data));
}, []);

// Display: "You have {usage.remaining.chat_requests} requests left today"
```

### Gemini API Usage Dashboard

Monitor your overall API usage at: https://aistudio.google.com/app/apikey

**What to watch**:
- Daily request count (should not spike unexpectedly)
- Token usage trends
- Error rates (high errors = potential attack)

**Set up alerts** (manual):
1. Check dashboard daily for first week
2. Note normal usage patterns
3. Watch for 2-3x spikes (indicates abuse)

### Cost Protection Configuration Guide

**For portfolio/demo apps** (current settings):
```python
DAILY_CHAT_LIMIT_PER_IP = 100        # Allows 10-20 users/day
DAILY_UPLOAD_LIMIT_PER_IP = 20       # Reasonable for demos
DAILY_TOKEN_LIMIT_PER_IP = 10000     # ~10-20 conversations
```

**For production apps** (stricter):
```python
DAILY_CHAT_LIMIT_PER_IP = 50         # Tighter control
DAILY_UPLOAD_LIMIT_PER_IP = 10       # Limit document uploads
DAILY_TOKEN_LIMIT_PER_IP = 5000      # ~5-10 conversations
RATE_LIMIT_CHAT = "5/minute"         # Slower rate
```

**For high-traffic apps** (with authentication):
```python
# Remove IP-based limits, use user-based limits instead
# Require login for API access
# Track usage per user ID, not IP
# Consider paid Gemini API tier
```

### What to Do If You See Abuse

**Signs of abuse**:
- Sudden spike in requests (10x normal)
- Same IP hitting daily limit repeatedly
- Multiple IPs from same region/pattern
- Gemini quota exhausted unexpectedly

**Immediate actions**:
1. **Check `/api/usage` endpoint** - Which IPs are using the most?
2. **Tighten limits temporarily**:
   ```python
   DAILY_CHAT_LIMIT_PER_IP = 20  # Reduce from 100
   DAILY_TOKEN_LIMIT_PER_IP = 2000  # Reduce from 10000
   ```
3. **Add IP blocklist** (if specific IPs abusing):
   ```python
   # In main.py
   BLOCKED_IPS = ["1.2.3.4", "5.6.7.8"]

   @app.middleware("http")
   async def block_ips(request: Request, call_next):
       if request.client.host in BLOCKED_IPS:
           return JSONResponse({"detail": "Blocked"}, status_code=403)
       return await call_next(request)
   ```
4. **Rotate API key** if quota exhausted
5. **Consider adding CAPTCHA** for public access

### Estimated Costs (If You Upgrade from Free Tier)

Gemini API pricing (as of 2026):
- **Free tier**: 1M tokens/day, 15 RPM
- **Paid tier**: ~$0.00025 per 1K tokens

With current protection (10K tokens/IP/day):
- 100 users/day = 1M tokens = **FREE**
- 1,000 users/day = 10M tokens = **~$2.50/day** (~$75/month)
- 10,000 users/day = 100M tokens = **~$25/day** (~$750/month)

**Recommendation**: Keep free tier limits until you have 50+ daily users, then consider upgrade.

---

## 🛡️ Additional Production Security Recommendations

### For Public Deployment:

1. **Add authentication** (if handling sensitive data)
   - Implement user login (OAuth, JWT)
   - Restrict API access to authenticated users
   - Consider API key authentication for programmatic access

2. **Enable HTTPS only** (already configured in Render)
   - Force SSL redirect
   - HSTS headers (already implemented)

3. **Add request logging**
   - Log all API requests (without sensitive data)
   - Monitor for suspicious patterns
   - Set up alerts for anomalies

4. **Implement request signing** (advanced)
   - HMAC-based request signatures
   - Prevents request tampering

5. **Add virus scanning for uploads**
   ```bash
   # Install ClamAV
   pip install clamd

   # In document_processor.py
   import clamd
   cd = clamd.ClamdUnixSocket()
   scan_result = cd.scan_stream(file_content)
   ```

6. **Database for persistent storage** (optional)
   - Move vector store to persistent DB (Pinecod, Qdrant)
   - Encrypt data at rest
   - Regular backups

7. **Regular dependency updates**
   ```bash
   pip install --upgrade -r requirements.txt
   npm audit fix
   ```

8. **Security scanning**
   ```bash
   # Python security check
   pip install safety
   safety check

   # Dependency vulnerabilities
   pip install pip-audit
   pip-audit
   ```

---

## 📋 Security Checklist for Deployment

Before deploying to production:

- [ ] `.env` file is in `.gitignore`
- [ ] API key is set as environment variable on Render (not in code)
- [ ] CORS origins updated to production URL
- [ ] Rate limiting enabled and tested
- [ ] File upload limits configured appropriately
- [ ] Security headers verified (check with https://securityheaders.com)
- [ ] HTTPS enforced (automatically done by Render)
- [ ] Error messages don't leak sensitive info
- [ ] Logs don't contain API keys or sensitive data
- [ ] Monitoring/alerting configured for usage spikes
- [ ] Backup API key created (stored securely offline)

---

## 🔍 Security Testing

### Test Rate Limiting:
```bash
# Send 15 requests rapidly (should get 429 after 10th)
for i in {1..15}; do
  curl -X POST "http://localhost:8000/api/chat/stream" \
    -H "Content-Type: application/json" \
    -d '{"message":"test","conversation_history":[],"use_rag":false}' &
done
```

### Test File Upload Security:
```bash
# Test path traversal (should fail)
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@test.pdf" \
  -F "filename=../../../etc/passwd"

# Test oversized file (should fail if > 10MB)
dd if=/dev/zero of=large.pdf bs=1M count=11
curl -X POST "http://localhost:8000/api/upload" -F "file=@large.pdf"
```

### Test Input Sanitization:
```bash
# Test XSS attempt (should be sanitized)
curl -X POST "http://localhost:8000/api/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"message":"<script>alert(1)</script>","conversation_history":[],"use_rag":false}'
```

---

## 📞 Security Issue Reporting

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. Email security concerns to: your-email@example.com
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Google AI API Security](https://ai.google.dev/gemini-api/docs/api-key)
- [Render Security](https://render.com/docs/security)

---

**Last updated**: 2026-01-16
**Security version**: 1.0.0
