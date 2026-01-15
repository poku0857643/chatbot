# Cost Protection Guide: Preventing API Abuse on Render

## Problem

When you deploy your RAG chatbot publicly on Render, **anyone can access it**. Attackers can:

1. **Exhaust your Gemini API free tier quota** (1M tokens/day)
2. **Generate unexpected costs** if you upgrade to paid tier
3. **Use multiple IPs** (VPNs, proxies) to bypass simple rate limiting
4. **Slowly drain quota** over hours/days to avoid detection

**Example attack**:
- Attacker uses 10 different VPNs
- Each IP sends 100 requests/day (within rate limit!)
- Total: 1,000 requests/day from different IPs
- Result: Your quota exhausted, app broken for real users

## Solution: Multi-Layer Protection

Your chatbot now has **3 layers of protection**:

### Layer 1: Rate Limiting (Per-Minute)
**File**: `main.py` + `slowapi` library

```python
RATE_LIMIT_CHAT = "10/minute"      # Max 10 chat requests per minute per IP
RATE_LIMIT_UPLOAD = "5/minute"     # Max 5 uploads per minute per IP
```

**What it stops**: Rapid-fire bot attacks, accidental loops

**What it doesn't stop**: Slow, distributed attacks over hours/days

### Layer 2: Daily Quotas (Per-IP)
**File**: `app/middleware/cost_protection.py`

```python
DAILY_CHAT_LIMIT_PER_IP = 100      # Max 100 chats per day per IP
DAILY_UPLOAD_LIMIT_PER_IP = 20     # Max 20 uploads per day per IP
DAILY_TOKEN_LIMIT_PER_IP = 10000   # Max 10,000 tokens per day per IP
```

**How it works**:
1. Tracks every request by IP address
2. Counts requests and tokens used per IP per day
3. Blocks IP when daily limit exceeded
4. Resets at midnight UTC

**Math**:
- Gemini free tier: 1,000,000 tokens/day total
- Per-IP limit: 10,000 tokens/day
- **Supports ~100 concurrent users/day** = FREE ✅
- Even if attacker uses 10 VPNs = 100K tokens = Still under limit ✅

### Layer 3: Burst Detection (Anti-Bot)
**File**: `app/middleware/cost_protection.py`

```python
# Detects suspicious patterns
- More than 5 requests in 10 seconds → BLOCK
- More than 20 requests in 1 minute → BLOCK
```

**What it stops**: Bots, scripts, automated attacks

## How It Works Technically

### 1. When User Sends a Chat Request

```python
# Step 1: Check cost limits BEFORE calling Gemini API
client_ip = await check_cost_limits(
    request=request,
    endpoint="chat",
    message=chat_request.message  # Used for token estimation
)

# Step 2: Estimate tokens (1 token ≈ 4 characters)
estimated_tokens = len(message) // 4

# Step 3: Check if adding these tokens would exceed daily limit
if daily_tokens[ip] + estimated_tokens > 10000:
    raise HTTPException(429, "Daily token limit exceeded")

# Step 4: If OK, call Gemini API
response = await gemini_api.generate(message)

# Step 5: Record actual usage
record_usage(client_ip, "chat", actual_tokens)
```

### 2. Data Storage (In-Memory)

```python
# Stored in RAM (per server instance)
daily_requests = {
    "203.0.113.42": {
        "2026-01-16": 42,  # 42 requests today
    }
}

daily_tokens = {
    "203.0.113.42": {
        "2026-01-16": 5230,  # 5,230 tokens used today
    }
}

# Auto-cleanup: Deletes data older than 2 days every hour
```

**Limitations**:
- ✅ **Works perfectly on Render free tier** (single instance)
- ⚠️ If you scale to multiple server instances, migrate to Redis:
  ```python
  import redis
  r = redis.Redis()
  r.incr(f"daily:{ip}:{date}")
  r.expire(f"daily:{ip}:{date}", 86400)  # Auto-delete after 24h
  ```

## Monitoring Your API Usage

### 1. Check Usage via API Endpoint

```bash
# Check your current usage
curl https://your-app.onrender.com/api/usage
```

**Response**:
```json
{
  "client_ip": "203.0.113.42",
  "daily_chat_requests": 42,
  "daily_upload_requests": 3,
  "daily_tokens_used": 5230,
  "limits": {
    "chat_requests_per_day": 100,
    "upload_requests_per_day": 20,
    "tokens_per_day": 10000
  },
  "remaining": {
    "chat_requests": 58,
    "upload_requests": 17,
    "tokens": 4770
  }
}
```

### 2. Monitor Gemini API Dashboard

Visit: https://aistudio.google.com/app/apikey

**Daily checklist** (first 2 weeks):
- [ ] Check total requests/day (should be < 1000 for portfolio)
- [ ] Check total tokens/day (should be < 100K for portfolio)
- [ ] Look for sudden spikes (2-3x normal = potential abuse)

**Set calendar reminder**: Check every Monday

### 3. Add Usage Display to Frontend (Optional)

```javascript
// In your React app
import { useState, useEffect } from 'react';

function UsageDisplay() {
  const [usage, setUsage] = useState(null);

  useEffect(() => {
    fetch('/api/usage')
      .then(res => res.json())
      .then(data => setUsage(data));
  }, []);

  if (!usage) return null;

  return (
    <div className="usage-info">
      ⏱️ {usage.remaining.chat_requests} requests remaining today
      <small>(Resets at midnight UTC)</small>
    </div>
  );
}
```

## What Happens When Limits Are Exceeded

### User sees this error:

```json
{
  "detail": "Daily limit exceeded. You can make 100 chat requests per day. Try again tomorrow.",
  "headers": {
    "Retry-After": "43200"  // Seconds until midnight UTC
  }
}
```

### In the browser:
```
HTTP 429 Too Many Requests
Daily limit exceeded. Try again tomorrow.
```

### Frontend can handle this:
```javascript
try {
  const response = await fetch('/api/chat/stream', {...});
  if (response.status === 429) {
    const error = await response.json();
    alert(error.detail);  // "Daily limit exceeded..."
  }
} catch (err) {
  console.error(err);
}
```

## Adjusting Limits for Your Use Case

### Portfolio/Demo (Current Settings) ✅
**Goal**: Show off project, handle light traffic

```python
DAILY_CHAT_LIMIT_PER_IP = 100        # ~10 users trying it out
DAILY_TOKEN_LIMIT_PER_IP = 10000     # ~10-20 conversations per user
RATE_LIMIT_CHAT = "10/minute"        # Allows smooth demo
```

**Supports**: 10-50 users/day comfortably

### Production App (Stricter)
**Goal**: Control costs, prevent abuse

```python
DAILY_CHAT_LIMIT_PER_IP = 50         # Tighter control
DAILY_TOKEN_LIMIT_PER_IP = 5000      # ~5-10 conversations
RATE_LIMIT_CHAT = "5/minute"         # Slower rate
```

### High-Traffic App (User Authentication Required)
**Goal**: Scale to 1000+ users

```python
# Remove IP-based limits
# Add user authentication (JWT)
# Track quota per user ID, not IP
# Consider paid Gemini tier ($0.00025/1K tokens)
```

## What If Someone Abuses It?

### Signs of Abuse:
- ✅ Gemini dashboard shows 10x spike in requests
- ✅ Single IP hitting limit repeatedly every day
- ✅ Multiple IPs from same ASN (datacenter/VPN provider)
- ✅ Quota exhausted faster than expected

### Immediate Actions:

**1. Identify abusive IPs** (check server logs):
```bash
# On Render, view logs
# Look for multiple 429 errors from same IPs
grep "429" logs.txt | cut -d' ' -f1 | sort | uniq -c | sort -nr
```

**2. Block specific IPs** (temporary):
```python
# In main.py
BLOCKED_IPS = ["1.2.3.4", "5.6.7.8"]

@app.middleware("http")
async def block_ips(request: Request, call_next):
    client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0]
    if client_ip in BLOCKED_IPS:
        return JSONResponse({"detail": "Access denied"}, status_code=403)
    return await call_next(request)
```

**3. Tighten limits temporarily**:
```python
# Reduce limits by 50% for 24 hours
DAILY_CHAT_LIMIT_PER_IP = 50
DAILY_TOKEN_LIMIT_PER_IP = 5000
```

**4. Rotate API key**:
- Go to https://aistudio.google.com/app/apikey
- Create new key
- Update Render environment variable
- Delete old key

**5. Add CAPTCHA** (if abuse continues):
```bash
pip install fastapi-recaptcha
# Requires Google reCAPTCHA setup
```

## Cost Estimates (If You Upgrade)

### Gemini API Pricing:
- **Free tier**: 1M tokens/day, 15 RPM
- **Paid tier**: ~$0.00025 per 1K tokens

### With Your Protection (10K tokens/IP/day):

| Daily Users | Tokens/Day | Cost/Day | Cost/Month |
|-------------|------------|----------|------------|
| 100         | 1M         | **FREE** | **$0**     |
| 1,000       | 10M        | $2.50    | $75        |
| 10,000      | 100M       | $25      | $750       |

**Recommendation**:
- Keep free tier until you have 50+ daily users
- Current protection ensures you won't accidentally hit paid tier

## Testing Cost Protection

### Test 1: Rate Limiting
```bash
# Send 15 rapid requests (should get 429 after 10th)
for i in {1..15}; do
  curl -X POST "http://localhost:8000/api/chat/stream" \
    -H "Content-Type: application/json" \
    -d '{"message":"test","conversation_history":[],"use_rag":false}' &
done
```

### Test 2: Daily Limit
```bash
# Simulate 101 requests (should fail on 101st)
for i in {1..101}; do
  echo "Request $i"
  curl -X POST "http://localhost:8000/api/chat/stream" \
    -H "Content-Type: application/json" \
    -d '{"message":"test","conversation_history":[],"use_rag":false}'
  sleep 7  # Avoid per-minute rate limit
done
```

### Test 3: Token Limit
```bash
# Send very long message (10K+ tokens)
python3 << 'EOF'
import requests

# Generate message that uses ~15K tokens (exceeds 10K limit)
long_message = "Hello world! " * 10000  # ~120K characters = ~30K tokens

response = requests.post(
    "http://localhost:8000/api/chat/stream",
    json={
        "message": long_message,
        "conversation_history": [],
        "use_rag": False
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
EOF
```

### Test 4: Usage Endpoint
```bash
# Check your usage
curl http://localhost:8000/api/usage | jq
```

## FAQs

### Q: Why not just use authentication instead of IP limits?
**A**: IP limits work for public demos without requiring signup. You can add authentication later for production.

### Q: What if legitimate users share an IP (office WiFi, university)?
**A**: Unlikely for portfolio projects. If it becomes an issue, increase limits or add user authentication.

### Q: Can attackers bypass this with unlimited VPNs?
**A**: Yes, but:
- Each VPN gets only 10K tokens/day
- Would need 100 VPNs to exhaust 1M free tier
- Most attackers won't bother for a chatbot
- If they do, add CAPTCHA or authentication

### Q: Does this work on Render free tier?
**A**: Yes! In-memory tracking works perfectly for single instance. If you scale to multiple instances, migrate to Redis.

### Q: How much does Redis cost on Render?
**A**: ~$7/month for Redis instance. Only needed if you scale beyond free tier.

## Summary

✅ **Your chatbot is now protected against**:
- Rapid bot attacks (rate limiting)
- Single-user quota exhaustion (daily limits per IP)
- Distributed VPN attacks (10K tokens/IP limit)
- Cost overruns (token estimation)

✅ **You can safely deploy to Render** without worrying about:
- Unexpected Gemini API bills
- Quota exhaustion from abuse
- App breaking from single malicious user

✅ **Monitoring is easy**:
- `/api/usage` endpoint shows real-time stats
- Gemini dashboard shows overall usage
- Automatic cleanup prevents memory bloat

🚀 **Ready to deploy!** Follow `deploy_instructions.md` to go live.
