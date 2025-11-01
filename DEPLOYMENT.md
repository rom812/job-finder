# Deployment Guide

This guide explains how to deploy the Job Finder application to production.

## Architecture

- **Frontend**: React + Vite → Deploy to Vercel
- **Backend**: Python Flask API → Deploy to Railway/Render

---

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account (free tier available)
- Git repository pushed to GitHub

### Steps

1. **Go to [Vercel](https://vercel.com)**
   - Sign in with GitHub

2. **Import Project**
   - Click "Add New..." → "Project"
   - Select your `job-finder` repository
   - **IMPORTANT**: Set root directory to `frontend`

3. **Configure Build Settings**
   - Framework Preset: **Vite**
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

4. **Add Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add the following:

   ```
   VITE_API_URL=https://your-backend-url.railway.app
   ```

   (You'll get this URL after deploying the backend)

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your frontend will be live at `https://your-project.vercel.app`

### Update Backend URL After Backend Deployment

After deploying the backend (see below), you need to:
1. Go to Vercel → Your Project → Settings → Environment Variables
2. Update `VITE_API_URL` to your actual Railway/Render backend URL
3. Redeploy (Vercel will auto-deploy on git push)

---

## Backend Deployment (Railway)

### Prerequisites
- Railway account (free tier: $5/month credit)
- Git repository pushed to GitHub

### Steps

1. **Go to [Railway](https://railway.app)**
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `job-finder` repository

3. **Configure Service**
   - Railway will auto-detect Python
   - It will use the `Procfile` automatically

4. **Add Environment Variables**

   **REQUIRED API Keys** (get from your .env file):
   ```
   OPENAI_API_KEY=sk-...
   FIRECRAWL_API_KEY=fc-...
   BRAVE_SEARCH_API_KEY=...
   RAPIDAPI_KEY=...
   ```

   **Optional (if you want news search)**:
   ```
   BING_API_KEY=...
   ```

5. **Configure Port**
   - Railway automatically sets `PORT` environment variable
   - Our `Procfile` uses this automatically

6. **Deploy**
   - Railway will automatically deploy
   - Wait 3-5 minutes
   - You'll get a URL like: `https://job-finder-production.up.railway.app`

7. **Enable Public Domain**
   - Go to Settings → Networking
   - Click "Generate Domain"
   - Copy this URL - you'll need it for the frontend

### Important Notes

- **Free Tier Limits**: Railway gives $5/month credit (≈500 hours)
- **Cold Starts**: Free tier apps may sleep after inactivity
- **API Costs**: OpenAI/FireCrawl usage will cost extra (not covered by Railway)

---

## Alternative: Backend Deployment (Render)

If you prefer Render.com (also has free tier):

1. **Go to [Render](https://render.com)**
   - Sign in with GitHub

2. **Create New Web Service**
   - Select `job-finder` repository
   - Name: `job-finder-api`
   - Environment: **Python**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python api/server.py --host 0.0.0.0 --port $PORT --no-load`

3. **Add Environment Variables**
   - Same as Railway (see above)

4. **Deploy**
   - Free tier URL: `https://job-finder-api.onrender.com`

### Render Free Tier Notes
- Apps sleep after 15 min of inactivity
- First request after sleep takes 30-60 seconds (cold start)
- 750 hours/month free

---

## After Deployment

### Update Frontend with Backend URL

1. Go to Vercel → Settings → Environment Variables
2. Set `VITE_API_URL` to your backend URL:
   ```
   VITE_API_URL=https://job-finder-production.up.railway.app
   ```
3. Redeploy frontend (automatic on next git push)

### Update CORS in Backend

If you get CORS errors, the backend already has CORS enabled (`CORS(app)` in `api/server.py`).

### Test the Deployment

1. Visit your Vercel frontend URL
2. Click "New Search"
3. Fill in job search details
4. Submit and verify it connects to backend

---

## Deployment Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Railway/Render
- [ ] Environment variables configured (API keys)
- [ ] Frontend `VITE_API_URL` points to backend
- [ ] Test: Can create new search
- [ ] Test: Jobs are displayed
- [ ] Test: Company insights show up

---

## Cost Estimate

### Monthly Costs (Estimated)

**Infrastructure** (FREE for demo/portfolio):
- Vercel: Free tier (hobby projects)
- Railway: $5 credit/month (enough for low traffic)
- OR Render: 750 hours/month free

**API Usage** (Pay-as-you-go):
- OpenAI GPT-4o-mini: ~$0.03-0.05 per search
- OpenAI Embeddings: ~$0.002 per search
- FireCrawl: Free tier (100 requests/month), then $0.50/100 requests
- Brave Search: 1,000 free requests/month
- JSearch (RapidAPI): 100 free requests/month

**Example**: 20 searches/month = ~$1-2 in API costs

---

## Troubleshooting

### Frontend can't connect to backend
- Check `VITE_API_URL` environment variable in Vercel
- Check backend logs in Railway/Render
- Verify CORS is enabled in backend

### Backend crashes on start
- Check environment variables are set correctly
- Check Railway/Render logs for errors
- Verify all API keys are valid

### "No jobs found" error
- Check API keys (JSearch, Brave Search, FireCrawl)
- Check backend logs for API errors
- Try a different job search query

---

## Next Steps

After successful deployment:

1. **Add to Resume/LinkedIn**:
   - Live Demo: `https://your-app.vercel.app`
   - GitHub: `https://github.com/your-username/job-finder`

2. **Add Screenshots** to README

3. **Monitor Usage**:
   - Railway/Render dashboard for uptime
   - OpenAI usage dashboard for API costs

4. **Optional Improvements**:
   - Add Redis caching to reduce API calls
   - Add user authentication
   - Add job application tracking
   - Set up monitoring/alerts

---

## Questions?

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs