# Frontend Deployment to Railway - Step by Step

Complete guide to deploy the React frontend to Railway.

## Prerequisites

✅ Backend deployed and running on Railway
✅ PostgreSQL database migrated
✅ Backend URL: `https://spendsense-production-bf62.up.railway.app`

---

## Step 1: Create Frontend Service

1. Go to https://railway.app/dashboard
2. Click on your **spendsense** project
3. Click **"+ New"** (top right)
4. Select **"GitHub Repo"**
5. Choose your **`spendsense`** repository (same repo as backend)
6. Railway will create a new service

---

## Step 2: Configure Frontend Service

Click on the **new service**, then go to **"Settings"** tab:

### Service Name
Change to: **`frontend`**

### Root Directory
Set to:
```
spendsense/ui
```

### Watch Paths
Set to:
```
spendsense/ui/**
```

This ensures Railway only redeploys frontend when frontend code changes.

---

## Step 3: Configure Build Settings

Still in **"Settings"** → scroll to **"Deploy"** section:

### Build Command
```
npm install && npm run build
```

### Start Command
```
npx serve -s dist -l $PORT
```

### Install Command (optional, Railway auto-detects)
```
npm install
```

Click **Save** or settings auto-save.

---

## Step 4: Add Environment Variable

Go to **"Variables"** tab:

1. Click **"+ New Variable"**
2. Add:
   ```
   VITE_API_URL=https://spendsense-production-bf62.up.railway.app
   ```
3. Click **"Add"**

This tells the frontend where to find the backend API.

---

## Step 5: Deploy Frontend

Railway will automatically trigger a deployment.

### Monitor Deployment:
1. Go to **"Deployments"** tab
2. Click on the active deployment
3. Watch the build logs

**Expected build time:** 2-3 minutes

**Look for:**
```
✓ Building frontend...
✓ npm install
✓ npm run build
✓ vite build
✓ Build complete
```

---

## Step 6: Generate Frontend Domain

After deployment succeeds:

1. Go to **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. Enter target port: **Leave blank** (Railway auto-detects)
4. Click **"Generate Domain"**
5. **Copy the frontend URL** (e.g., `https://spendsense-frontend-production-xxxx.up.railway.app`)

---

## Step 7: Update Backend CORS

Now update the backend to allow requests from your frontend:

1. Go to **backend service** → **"Variables"** tab
2. Find **`ALLOWED_ORIGINS`**
3. Update to:
   ```
   ALLOWED_ORIGINS=https://your-frontend-url.up.railway.app,http://localhost:3000
   ```
   (Replace `your-frontend-url.up.railway.app` with your actual frontend URL)
4. Backend will auto-redeploy (~1 minute)

---

## Step 8: Test the Application

### Test Backend Directly
Visit: `https://spendsense-production-bf62.up.railway.app/docs`
- ✅ Should show FastAPI Swagger UI
- ✅ Try an endpoint like `/api/personas`

### Test Frontend
Visit: `https://your-frontend-url.up.railway.app`

**You should see:**
- ✅ SpendSense frontend loads
- ✅ No CORS errors in browser console (F12)
- ✅ Data loads from backend
- ✅ Navigation works

### Test API Connection
1. Open browser console (F12)
2. Go to **Network** tab
3. Reload the frontend
4. Look for API calls to `https://spendsense-production-bf62.up.railway.app`
5. ✅ Requests should return 200 OK

---

## Troubleshooting

### Frontend Build Fails

**Check build logs in Railway:**
- Look for npm install errors
- Check if package.json is correct
- Verify Node version compatibility

**Common fixes:**
- Ensure root directory is `spendsense/ui`
- Check that `package.json` exists in that path

### Frontend Shows Blank Page

**Check browser console (F12):**
- Look for JavaScript errors
- Check if assets loaded correctly

**Verify:**
- Build command created `dist` folder
- Start command is serving from `dist`

### CORS Errors

**Error:** `Access to fetch blocked by CORS policy`

**Fix:**
1. Verify backend `ALLOWED_ORIGINS` includes frontend URL
2. Check backend redeployed after changing CORS
3. Clear browser cache and try again

### API Calls Fail (404, 500)

**Check:**
- `VITE_API_URL` is set correctly in frontend
- Backend is running and accessible
- Network tab shows correct API URL being called

---

## Verification Checklist

After deployment, verify:

- [ ] Frontend service created
- [ ] Root directory set to `spendsense/ui`
- [ ] Build command: `npm install && npm run build`
- [ ] Start command: `npx serve -s dist -l $PORT`
- [ ] `VITE_API_URL` environment variable set
- [ ] Deployment succeeded (green checkmark)
- [ ] Frontend domain generated
- [ ] Backend CORS updated with frontend URL
- [ ] Backend redeployed
- [ ] Frontend loads in browser
- [ ] No CORS errors
- [ ] API calls work
- [ ] Data displays correctly

---

## Production URLs

After successful deployment, you'll have:

- **Backend API:** https://spendsense-production-bf62.up.railway.app
- **Frontend App:** https://spendsense-frontend-production-xxxx.up.railway.app
- **Database:** PostgreSQL on Railway (internal)

---

## Next Steps

1. ✅ Test all features
2. ✅ Add custom domain (optional)
3. ✅ Set up monitoring/alerting
4. ✅ Configure environment-specific settings
5. ✅ Document deployment process for team

---

🎉 **Congratulations!** Your full-stack SpendSense application is now deployed on Railway!
