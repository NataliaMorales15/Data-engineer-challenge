# 🚀 Step-by-Step Setup Guide

Follow these steps to get your project up and running!

---

## ✅ Step 1: Prepare Your Machine

### Check Python Version
```bash
python --version
# Should be 3.9 or higher
```

### Create Project Folder
```bash
# Navigate to where you want to keep the project
cd ~

# Create directory
mkdir globant_challenge
cd globant_challenge
```

---

## ✅ Step 2: Initialize Virtual Environment

### Create Virtual Environment
```bash
python -m venv venv
```

### Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

**Verify Activation:**
You should see `(venv)` prefix in your terminal:
```
(venv) user@machine globant_challenge $
```

---

## ✅ Step 3: Install Dependencies

```bash
pip install --upgrade pip

pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed fastavro-1.8.0 flask-2.3.0 pandas-2.0.0 sqlalchemy-2.0.0 ...
```

---

## ✅ Step 4: Prepare Your CSV Files

Copy your CSV files to the `data/` folder:

```bash
# Create data directory
mkdir -p data

# Copy files
cp /path/to/departments.csv data/
cp /path/to/jobs.csv data/
cp /path/to/hired_employees__1_.csv data/
```

**Verify Files:**
```bash
ls -la data/
# Should show:
# departments.csv
# jobs.csv
# hired_employees__1_.csv
```

---

## ✅ Step 5: Create Required Directories

```bash
mkdir -p backup logs
```

---

## ✅ Step 6: Start the API Server

```bash
python src/main.py
```

**Expected Output:**
```
============================================================
🚀 GLOBANT DATA ENGINEER CHALLENGE - DATA INGESTION
============================================================

📁 Creating project directories...
✅ Directories created

🗄️  Initializing database...
✅ Database initialized

📥 Loading historical data from CSV files...
✅ Data loaded successfully!
   - Departments: 12 records
   - Jobs: 320 records
   - Hired Employees: 37544 records

🔍 Checking data quality...
✅ Data quality check complete:
   - Valid employees: 37000 (approx)
   - Invalid employees: 544 (approx)

============================================================
🌐 STARTING REST API SERVER
============================================================

✅ API running at: http://localhost:5000
...
```

---

## ✅ Step 7: Test the API

In a **new terminal** (keep the API running), test the health endpoint:

```bash
curl http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "message": "API is running",
  "database": "connected"
}
```

---

## ✅ Step 8: Review Error Log

Check if there are any data quality issues:

```bash
cat logs/error.log | head -20
```

This shows you invalid records that were rejected during data loading.

---

## 🎯 Common First Commands

### 1. Check Database Statistics
```bash
curl http://localhost:5000/api/stats
```

### 2. Ingest a Single Department
```bash
curl -X POST http://localhost:5000/api/departments \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"id": 100, "department": "Test Department"}
    ]
  }'
```

### 3. Ingest a Valid Employee
```bash
curl -X POST http://localhost:5000/api/hired_employees \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "id": 50000,
        "name": "Test Employee",
        "datetime": "2021-05-15T10:30:00Z",
        "department_id": 1,
        "job_id": 1
      }
    ]
  }'
```

### 4. Test with Invalid Data (Should Be Rejected)
```bash
curl -X POST http://localhost:5000/api/hired_employees \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "id": 50001,
        "name": "Invalid Employee",
        "datetime": "INVALID-DATE",
        "department_id": 1,
        "job_id": 1
      }
    ]
  }'
```

Expected response shows rejection with error details.

---

## 🗄️ Project Structure After Setup

```
globant_challenge/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── validation.py
│   ├── api.py
│   └── backup_restore.py
│
├── data/
│   ├── departments.csv
│   ├── jobs.csv
│   └── hired_employees__1_.csv
│
├── backup/                  # (Auto-created)
├── logs/                    # (Auto-created)
│   └── error.log           # (Auto-created)
│
├── venv/                    # Virtual environment
├── requirements.txt
├── .gitignore
├── README.md
├── SETUP_GUIDE.md          # This file
└── globant_challenge.db    # (Auto-created)
```

---

## 🔍 Troubleshooting Setup

### Error: "No module named 'flask'"

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Error: "Port 5000 already in use"

**Solution:**
```bash
# Find process using port 5000 (macOS/Linux)
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or modify port in main.py (change port=5000 to port=5001)
```

---

### Error: "CSV files not found"

**Solution:**
```bash
# Verify files are in data/ folder
ls -la data/

# If not, copy them
cp /your/path/departments.csv data/
cp /your/path/jobs.csv data/
cp /your/path/hired_employees__1_.csv data/
```

---

## ✨ You're All Set!

Your API is now running and ready to:
- ✅ Ingest data via REST API
- ✅ Validate records
- ✅ Log errors
- ✅ Backup tables
- ✅ Restore from backups

**Next Steps:**
1. Read the README.md for complete API documentation
2. Test all endpoints
3. Create backups
4. Experiment with data

**Happy coding! 🚀**
