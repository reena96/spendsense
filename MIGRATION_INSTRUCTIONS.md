# PostgreSQL Migration Instructions

Complete these steps to migrate your SQLite data to PostgreSQL on Railway.

## Prerequisites

✅ psycopg2-binary installed
✅ Migration script created
✅ SQLite backup saved
✅ PostgreSQL added to Railway

## Step 1: Link to Railway Project

Open your terminal and run:

```bash
cd /Users/reena/gauntletai/spendsense
railway link
```

**Select your project** when prompted (should be "spendsense")

## Step 2: Get DATABASE_URL

```bash
railway variables | grep DATABASE_URL
```

**Copy the full DATABASE_URL** value. It will look like:
```
DATABASE_URL=postgresql://postgres:password@containers-us-west-xxx.railway.app/railway
```

## Step 3: Run Migration Script

**Set the DATABASE_URL and run migration:**

```bash
# Activate virtual environment
source venv/bin/activate

# Set DATABASE_URL (replace with your actual URL from step 2)
export DATABASE_URL="postgresql://postgres:password@containers-us-west-xxx.railway.app/railway"

# Run migration
python scripts/migrate_sqlite_to_postgres.py
```

**When prompted "Continue? (yes/no):"** type `yes` and press Enter

## Step 4: Verify Migration

The script will show you a verification table:

```
✓ accounts           SQLite:   120 → PostgreSQL:   120
✓ transactions       SQLite:  5420 → PostgreSQL:  5420
✓ auth_audit_log     SQLite:    15 → PostgreSQL:    15
...
```

**All checkmarks should be ✓** - this means all data copied successfully!

## Step 5: Verify Backend is Using PostgreSQL

Railway should have automatically redeployed with the new code. Check:

1. Go to Railway → Backend service → Deployments
2. Latest deployment should show "Success"
3. In logs, you should see PostgreSQL connection (no more SQLite warnings)

## What's Next?

After successful migration:
- ✅ Backend will use PostgreSQL (persistent data!)
- ✅ Frontend deployment
- ✅ Full application testing

---

## Troubleshooting

### Error: "No module named 'psycopg2'"
```bash
source venv/bin/activate
pip install psycopg2-binary
```

### Error: "railway: command not found"
```bash
npm install -g @railway/cli
railway login --browserless
```

### Error: "could not connect to server"
- Check DATABASE_URL is correct
- Ensure PostgreSQL service is running in Railway
- Try again in a few minutes (Railway might be provisioning)

### Migration shows mismatched counts
- Don't panic! Note which tables
- Check Railway logs for errors
- Can re-run migration (it will overwrite)

---

## If Something Goes Wrong

Your data is safe! You have:
- ✅ Original SQLite: `data/processed/spendsense.db`
- ✅ Backup: `backups/spendsense_backup_20251110_022013.db`

You can always:
1. Keep using SQLite (revert code changes)
2. Try migration again
3. Ask for help!
