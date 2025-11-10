# Railway Deployment Guide for SpendSense

Complete guide to deploy the full-stack SpendSense application on Railway.

## Overview

Railway will host:
- **Backend**: Python FastAPI application with data science dependencies
- **Frontend**: React + Vite static site
- **Database**: PostgreSQL (Railway managed)

## Prerequisites

1. Railway account: https://railway.app
2. GitHub repository with your code
3. Railway CLI (optional): `npm install -g @railway/cli`

---

## Step 1: Initial Railway Setup

### 1.1 Create New Project

1. Go to https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select your `spendsense` repository
4. Railway will create a new project

### 1.2 Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will provision a PostgreSQL instance
4. Note: The `DATABASE_URL` will be automatically available to your services

---

## Step 2: Deploy Backend Service

### 2.1 Configure Backend Service

1. In Railway project, click **"+ New"** → **"GitHub Repo"**
2. Select your repository again (this creates a second service)
3. Click on the service → **"Settings"**
4. Configure:
   - **Service Name**: `spendsense-backend`
   - **Root Directory**: Leave empty (/)
   - **Build Command**: Leave default (Railway auto-detects)
   - **Start Command**: `uvicorn spendsense.api.main:app --host 0.0.0.0 --port $PORT`

### 2.2 Set Backend Environment Variables

In the backend service, go to **"Variables"** tab and add:

```bash
# Database (automatically available from PostgreSQL service)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Authentication
SECRET_KEY=<generate-a-secure-random-string-here>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS - Add your frontend URL (will set after frontend deploys)
ALLOWED_ORIGINS=https://your-frontend-name.up.railway.app
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.3 Deploy Backend

1. Railway will automatically deploy when you push to GitHub
2. Or manually trigger: Click **"Deploy"** button
3. Wait for deployment to complete (~3-5 minutes)
4. Get your backend URL: https://spendsense-backend.up.railway.app

---

## Step 3: Deploy Frontend Service

### 3.1 Create Frontend Service

1. In Railway project, click **"+ New"** → **"GitHub Repo"**
2. Select your repository (third service)
3. Click on the service → **"Settings"**
4. Configure:
   - **Service Name**: `spendsense-frontend`
   - **Root Directory**: `spendsense/ui`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: Leave empty (static site)

### 3.2 Configure as Static Site

In **"Settings"** → **"Deployment"**:
- **Static Site**: Enable
- **Output Directory**: `dist`

### 3.3 Set Frontend Environment Variables

In the frontend service, go to **"Variables"** tab and add:

```bash
# Point to your backend service
VITE_API_URL=https://spendsense-backend.up.railway.app
```

### 3.4 Deploy Frontend

1. Click **"Deploy"** button
2. Wait for build to complete (~2-3 minutes)
3. Get your frontend URL: https://spendsense-frontend.up.railway.app

---

## Step 4: Update CORS Configuration

Now that you have the frontend URL:

1. Go to backend service → **"Variables"**
2. Update `ALLOWED_ORIGINS` with your actual frontend URL:
   ```bash
   ALLOWED_ORIGINS=https://spendsense-frontend.up.railway.app
   ```
3. Backend will automatically redeploy

---

## Step 5: Database Setup

### 5.1 Run Migrations (if you have any)

Using Railway CLI:
```bash
railway login
railway link
railway run python -m spendsense.db.migrations
```

Or connect directly:
```bash
# Get DATABASE_URL from Railway Variables tab
export DATABASE_URL="postgresql://..."
python -m spendsense.db.migrations
```

### 5.2 Seed Initial Data (optional)

```bash
railway run python scripts/seed_database.py
```

---

## Step 6: Custom Domains (Optional)

### Add Custom Domain

1. Go to frontend service → **"Settings"** → **"Domains"**
2. Click **"Custom Domain"**
3. Add your domain: `app.yourdomain.com`
4. Update DNS records as shown
5. Update backend `ALLOWED_ORIGINS` to include custom domain

---

## Verification Checklist

After deployment, verify:

- [ ] Backend is responding: `https://your-backend.up.railway.app/docs`
- [ ] Frontend loads: `https://your-frontend.up.railway.app`
- [ ] API calls work from frontend
- [ ] Database connections successful
- [ ] Authentication flows work
- [ ] No CORS errors in browser console

---

## Monitoring & Logs

### View Logs
1. Click on any service
2. Go to **"Deployments"** tab
3. Click on latest deployment
4. View **"Logs"** section

### Metrics
- Railway provides CPU, Memory, Network usage
- Available in service **"Metrics"** tab

---

## Environment Variables Reference

### Backend Variables
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=https://your-frontend.railway.app
PORT=8000  # Auto-set by Railway
```

### Frontend Variables
```bash
VITE_API_URL=https://your-backend.railway.app
```

---

## Troubleshooting

### Build Fails

**Frontend build fails:**
```bash
# Check Node version in Railway settings
# Ensure package.json scripts are correct
# View build logs for specific errors
```

**Backend build fails:**
```bash
# Check requirements.txt has all dependencies
# Ensure Python version is 3.10+
# Check for missing system dependencies
```

### CORS Errors

```bash
# Verify ALLOWED_ORIGINS in backend includes frontend URL
# Check frontend VITE_API_URL is correct
# Ensure no trailing slashes in URLs
```

### Database Connection Fails

```bash
# Verify DATABASE_URL is set
# Check PostgreSQL service is running
# Ensure database migrations have run
```

### 502 Bad Gateway

```bash
# Backend might be crashing
# Check backend logs for errors
# Verify start command is correct
# Check PORT environment variable
```

---

## Cost Estimation

Railway Pricing (as of 2024):
- **Hobby Plan**: $5/month + usage
  - $0.000231/GB-hour (memory)
  - $0.000463/vCPU-hour
- **Free Trial**: $5 credit

Typical cost for SpendSense:
- Backend: ~$10-15/month (heavy dependencies)
- Frontend: ~$2-5/month
- PostgreSQL: ~$5/month
- **Total**: ~$20-25/month

---

## Alternative: Single Service Deployment

If you want to serve frontend from backend (simpler but less scalable):

1. Build frontend locally: `cd spendsense/ui && npm run build`
2. Copy `dist/` to backend static folder
3. Update FastAPI to serve static files
4. Deploy only backend service
5. Frontend available at: `https://backend.railway.app`

---

## Continuous Deployment

Railway auto-deploys on git push:

1. Push to GitHub: `git push origin main`
2. Railway detects changes
3. Rebuilds and redeploys affected services
4. Monitor deployment in Railway dashboard

---

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- SpendSense Issues: Create GitHub issue

---

## Next Steps

After successful deployment:
1. Set up monitoring (Railway provides basic metrics)
2. Configure alerting for service health
3. Set up automated backups for PostgreSQL
4. Add custom domain with SSL
5. Configure CI/CD for automated testing before deploy
