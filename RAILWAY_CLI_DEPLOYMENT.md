# Railway CLI Deployment Guide for SpendSense

Deploy your full-stack SpendSense application using Railway CLI - no GitHub OAuth required!

## Overview

This guide walks you through deploying:
- **Backend**: Python FastAPI application
- **Frontend**: React + Vite static site
- **Database**: PostgreSQL

All using the Railway CLI from your local machine.

---

## Prerequisites

- Node.js installed (for Railway CLI)
- Your SpendSense code on your local machine
- A valid email address

---

## Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

Verify installation:
```bash
railway --version
```

---

## Step 2: Login to Railway

### Login with Email (No GitHub Required)

```bash
railway login --browserless
```

**What happens:**
1. Railway will display a URL in your terminal
2. Copy the URL and open it in your browser
3. Enter your email address
4. Check your email for a magic link
5. Click the magic link to authenticate
6. Return to terminal - you're now logged in!

**Verify login:**
```bash
railway whoami
```

---

## Step 3: Create Railway Project

### Create New Project

```bash
# Navigate to your project root
cd /Users/reena/gauntletai/spendsense

# Initialize Railway project
railway init
```

**You'll be prompted:**
- **"Create a new project or select existing?"** → Choose **"Create new project"**
- **"Project name?"** → Enter: `spendsense`
- **"Environment?"** → Choose **"production"**

This creates a Railway project linked to your local directory.

---

## Step 4: Add PostgreSQL Database

```bash
railway add --database postgres
```

This provisions a PostgreSQL database in your Railway project.

**Get database URL:**
```bash
railway variables
```

You'll see `DATABASE_URL` listed - Railway automatically provides this to your services.

---

## Step 5: Deploy Backend Service

### 5.1 Create Backend Service

```bash
# Create backend service
railway service create backend
```

### 5.2 Set Backend Environment Variables

```bash
# Generate a secret key first
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy the output

# Set environment variables
railway variables set SECRET_KEY="<paste-your-generated-key-here>"
railway variables set ALGORITHM="HS256"
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"

# Database URL is automatically available from Postgres service
# CORS will be set after frontend deploys
```

### 5.3 Deploy Backend

```bash
# Deploy backend from current directory
railway up

# Watch deployment logs
railway logs
```

**Wait for deployment to complete** (~3-5 minutes due to data science dependencies).

### 5.4 Get Backend URL

```bash
# Generate public domain for backend
railway domain

# Copy the URL shown (e.g., backend-production-xxxx.up.railway.app)
```

**Test backend:**
```bash
curl https://your-backend-url.up.railway.app/docs
```

You should see the FastAPI Swagger documentation.

---

## Step 6: Deploy Frontend Service

### 6.1 Create Frontend Service

```bash
# Create frontend service
railway service create frontend
```

### 6.2 Configure Frontend Build

Railway needs to know how to build your frontend.

**Create a railway.toml for frontend service:**

```bash
cat > railway.frontend.toml << 'EOF'
[build]
builder = "NIXPACKS"
buildCommand = "cd spendsense/ui && npm install && npm run build"

[deploy]
startCommand = "npx serve -s spendsense/ui/dist -l $PORT"
EOF
```

### 6.3 Set Frontend Environment Variables

```bash
# Set API URL to point to backend
railway variables set VITE_API_URL="https://your-backend-url.up.railway.app"
```

**Replace `your-backend-url.up.railway.app` with actual backend URL from Step 5.4**

### 6.4 Deploy Frontend

```bash
# Deploy frontend
railway up

# Watch logs
railway logs
```

### 6.5 Get Frontend URL

```bash
# Generate public domain for frontend
railway domain

# Copy the URL shown
```

**Test frontend:**
Open the frontend URL in your browser.

---

## Step 7: Update Backend CORS

Now that frontend is deployed, update backend to allow frontend origin:

```bash
# Switch back to backend service
railway service

# Select "backend" from the list

# Set CORS origins
railway variables set ALLOWED_ORIGINS="https://your-frontend-url.up.railway.app"
```

Backend will automatically redeploy with new CORS settings.

---

## Step 8: Verification

### Check All Services

```bash
# List all services
railway status
```

You should see:
- ✅ backend (running)
- ✅ frontend (running)
- ✅ postgres (running)

### Test the Application

1. **Backend API**: Visit `https://your-backend-url.up.railway.app/docs`
2. **Frontend**: Visit `https://your-frontend-url.up.railway.app`
3. **Test API calls**: Use the frontend to ensure it can communicate with backend

---

## Useful Railway CLI Commands

### View Logs
```bash
# Current service logs
railway logs

# Follow logs in real-time
railway logs --follow

# Specific service logs
railway logs backend
railway logs frontend
```

### Manage Variables
```bash
# List all variables
railway variables

# Set a variable
railway variables set KEY=value

# Delete a variable
railway variables delete KEY
```

### Service Management
```bash
# List services
railway service

# Switch service
railway service frontend

# Service info
railway status
```

### Deployments
```bash
# Redeploy current service
railway up

# Check deployment status
railway status

# View specific deployment
railway deployment list
```

### Database Management
```bash
# Connect to PostgreSQL
railway connect postgres

# Run migrations
railway run python -m spendsense.db.migrations

# Seed data
railway run python scripts/seed_database.py
```

---

## Updating Your Application

### Method 1: Direct Upload (Recommended)

When you make code changes:

```bash
# Navigate to project root
cd /Users/reena/gauntletai/spendsense

# Switch to the service you want to update
railway service backend  # or frontend

# Deploy
railway up

# Watch deployment
railway logs --follow
```

### Method 2: Connect GitHub Later (Optional)

If you later want auto-deployments from GitHub:

```bash
# Link to GitHub repo
railway link

# Follow prompts to connect repository
```

This allows Railway to auto-deploy on git push.

---

## Environment Variables Reference

### Backend Service
```bash
SECRET_KEY=<generated-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=<automatically-provided-by-postgres-service>
ALLOWED_ORIGINS=https://your-frontend-url.up.railway.app
PORT=<automatically-set-by-railway>
```

### Frontend Service
```bash
VITE_API_URL=https://your-backend-url.up.railway.app
PORT=<automatically-set-by-railway>
```

---

## Troubleshooting

### CLI Not Authenticated
```bash
# Re-login
railway login --browserless
```

### Build Fails

**View build logs:**
```bash
railway logs
```

**Common issues:**
- Missing dependencies in `requirements.txt`
- Node version mismatch (specify in package.json)
- Build command incorrect

### Can't Access Service

**Check if domain is generated:**
```bash
railway domain
```

**If no domain exists:**
```bash
# Generate one
railway domain
```

### Database Connection Issues

**Verify database exists:**
```bash
railway variables | grep DATABASE_URL
```

**Connect to database:**
```bash
railway connect postgres
```

### Service Won't Start

**Check logs:**
```bash
railway logs --follow
```

**Common issues:**
- Wrong start command
- Missing environment variables
- Port not bound to `$PORT`

### Deploy Takes Too Long

Backend deployment is slow due to heavy dependencies (pandas, numpy, scipy).
- First deploy: 3-5 minutes
- Subsequent deploys: 2-3 minutes (cached layers)

**Monitor progress:**
```bash
railway logs --follow
```

---

## Project Structure in Railway

After following this guide, your Railway project will have:

```
spendsense (project)
├── backend (service)
│   ├── Environment: production
│   ├── Domain: backend-production-xxxx.up.railway.app
│   └── Variables: SECRET_KEY, ALLOWED_ORIGINS, DATABASE_URL
├── frontend (service)
│   ├── Environment: production
│   ├── Domain: frontend-production-xxxx.up.railway.app
│   └── Variables: VITE_API_URL
└── postgres (database)
    ├── Environment: production
    └── Provides: DATABASE_URL
```

---

## Cost Estimation

Railway charges based on usage:
- **Hobby Plan**: $5/month + usage
- **Backend**: ~$10-15/month (heavy dependencies)
- **Frontend**: ~$2-5/month
- **PostgreSQL**: ~$5/month
- **Total**: ~$20-25/month

**Monitor usage:**
```bash
railway status
```

Or check Railway dashboard: https://railway.app/dashboard

---

## Switching Between Services

Railway CLI context is per-directory. To manage different services:

```bash
# View current service
railway service

# Switch service
railway service backend
railway service frontend

# Or specify service in commands
railway logs backend
railway logs frontend
railway variables backend
```

---

## Rolling Back Deployments

If a deployment breaks something:

```bash
# List deployments
railway deployment list

# View specific deployment
railway deployment view <deployment-id>

# Rollback (redeploy previous version)
# Note: No built-in rollback, redeploy previous code
railway up
```

---

## Custom Domains (Optional)

Add your own domain:

```bash
# Switch to service (backend or frontend)
railway service frontend

# Add custom domain
railway domain add app.yourdomain.com

# Railway will provide DNS records
# Update your DNS provider with the records shown
```

---

## Deleting Resources

### Delete a Service
```bash
railway service delete <service-name>
```

### Delete Entire Project
```bash
railway delete
```

---

## Getting Help

- **Railway CLI docs**: https://docs.railway.app/develop/cli
- **Railway Discord**: https://discord.gg/railway
- **Check service status**: `railway status`
- **View logs**: `railway logs --follow`

---

## Next Steps After Deployment

1. ✅ Set up monitoring in Railway dashboard
2. ✅ Configure custom domain (optional)
3. ✅ Set up database backups
4. ✅ Add health check endpoints
5. ✅ Configure alerting for downtime
6. ✅ Run migrations and seed data
7. ✅ Test all functionality end-to-end

---

## Quick Command Reference

```bash
# Authentication
railway login --browserless
railway whoami

# Project management
railway init
railway status
railway delete

# Service management
railway service
railway service <name>
railway up
railway logs
railway logs --follow

# Variables
railway variables
railway variables set KEY=value
railway variables delete KEY

# Domains
railway domain
railway domain add <custom-domain>

# Database
railway add --database postgres
railway connect postgres
railway run <command>

# Deployment
railway up
railway deployment list
```

---

## Success Checklist

After completing this guide, verify:

- [ ] Railway CLI installed and authenticated
- [ ] Project created in Railway
- [ ] PostgreSQL database provisioned
- [ ] Backend service deployed and accessible
- [ ] Frontend service deployed and accessible
- [ ] Environment variables configured correctly
- [ ] CORS allows frontend to call backend
- [ ] No errors in service logs
- [ ] Application works end-to-end

Congratulations! Your SpendSense application is now deployed on Railway! 🎉
