# Quick Deploy to Render.com (FREE)

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
3. **Add to LinkedIn/Resume**
4. **Share with recruiters**

Your live URL is the best portfolio piece! 🎉
