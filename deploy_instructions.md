# Quick Deploy to Render.com (FREE)

## 🔒 Security First

**CRITICAL**: Your `GEMINI_API_KEY` is sensitive. Never commit it to GitHub or share it publicly.

- ✅ API key is already excluded by `.gitignore` (.env file)
- ✅ Only add API key as environment variable on Render (never in code)
- ✅ Rotate API key every 90 days: https://aistudio.google.com/app/apikey
- 📖 Read full security guide: `SECURITY.md`

---

## Step 1: Sign Up (2 minutes)
1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (easiest)

## Step 2: Deploy (5 minutes)
1. Click "New +" → "Web Service"
2. Connect GitHub repository: `poku0857643/chatbot`
3. Render auto-detects `render.yaml` ✅
4. Configure:
   - **Name**: `rag-chatbot` (or your choice)
   - **Region**: Oregon (US West) - closest to you
   - **Branch**: main
   - **Environment Variables**:
     - Click "Add Environment Variable"
     - Key: `GEMINI_API_KEY`
     - Value: [paste your actual API key from .env file]
     - ⚠️ **IMPORTANT**: This stays on Render only, never in GitHub

5. Click "Create Web Service"

## Step 3: Wait for Build (3-5 minutes)
- Render will build the Docker image
- Install dependencies
- Build React frontend
- Deploy automatically

## Step 4: Get Your URL
You'll get a URL like: `https://rag-chatbot-xxxx.onrender.com`

## Step 5: Test It
1. Visit your URL
2. Upload a test document
3. Ask a question
4. ✅ It works!

---

## ⚠️ Important Notes

### Free Tier Limitations:
- **Spins down after 15 minutes of inactivity**
- **Takes 30-60 seconds to wake up on first request**
- Perfect for portfolio (not for production traffic)

### Pro Tip:
Add this to your README:
```markdown
> ⚡ Note: Free tier spins down after inactivity. First load may take 30-60s.
```

### Cost:
- **$0/month** on free tier
- Upgrade to $7/month for always-on (optional, not needed for portfolio)

---

## Alternative: Railway.app (Also Free)

If Render doesn't work, try Railway:

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub"
4. Select `poku0857643/chatbot`
5. Add environment variable: `GEMINI_API_KEY=your_key`
6. Deploy (auto-detects Dockerfile)
7. Get URL: `https://chatbot-production-xxxx.up.railway.app`

Railway free tier: $5 credit/month (plenty for portfolio)

---

## After Deployment

1. **Test thoroughly** on desktop and mobile
2. **Update README.md** with live demo link
3. **Update CORS settings** in `app/middleware/settings/settings.py`:
   ```python
   CORS_ORIGINS = ["https://your-actual-url.onrender.com"]
   ```
   Then git push to redeploy.
4. **Add to LinkedIn/Resume**
5. **Share with recruiters**

Your live URL is the best portfolio piece! 🎉

---

## 🔒 Post-Deployment Security

### Verify Security Features

1. **Test rate limiting**:
   - Try sending 15+ rapid requests (should get 429 error after 10th)

2. **Check security headers**:
   - Visit: https://securityheaders.com
   - Enter your Render URL
   - Should see security headers enabled

3. **Monitor API usage**:
   - Go to https://aistudio.google.com/app/apikey
   - Check Gemini API usage dashboard
   - Watch for unexpected spikes

4. **Rotate API key** (recommended every 90 days):
   - Create new key at https://aistudio.google.com/app/apikey
   - Update environment variable on Render
   - Delete old key

### Security Checklist

- [ ] API key set as environment variable (not in code)
- [ ] `.env` file is NOT in your GitHub repo
- [ ] CORS origins updated to production URL
- [ ] Tested rate limiting works
- [ ] Verified HTTPS is enforced
- [ ] Bookmarked API key rotation date (90 days from now)

### Built-in Security Features

Your app includes:
- ✅ Rate limiting (10 chat/min, 5 uploads/min)
- ✅ Input sanitization (XSS protection)
- ✅ File upload validation (type, size, filename)
- ✅ Security headers (HSTS, CSP, X-Frame-Options)
- ✅ HTTPS only (enforced by Render)

📖 **Read the full security guide**: `SECURITY.md`
