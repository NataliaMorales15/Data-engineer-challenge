# 🚀 Globant Data Engineer Challenge - Data Ingestion & API

A complete proof-of-concept (PoC) for historical data migration, REST API data ingestion, validation, and AVRO backup/restore functionality.

**Status**: ✅ Ready for Production

---

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Data Validation Rules](#data-validation-rules)
- [Examples](#examples)
- [Backup & Restore](#backup--restore)
- [Architecture & Design Decisions](#architecture--design-decisions)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Challenge #1: Data Ingestion

✅ **Historical Data Migration**
- Load CSV files into SQLite database
- Support for 3 tables: departments, jobs, hired_employees

✅ **REST API for Data Ingestion**
- Separate endpoints per table (clean & maintainable)
- Batch ingestion (1-1000 rows per request)
- JSON request/response format
- Partial success handling (insert valid, reject invalid)

✅ **Data Validation**
- All 5 validation rules enforced
- Invalid records rejected & logged
- Detailed error messages in API responses
- Logging to file and database

✅ **Backup & Restore**
- Export tables to AVRO format
- Restore from AVRO backups
- Preserves data integrity

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9+
- pip (Python package manager)

### 2. Setup

```bash
# Clone or navigate to project directory
cd globant_challenge

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories (if not exists)
mkdir -p data backup logs

# Copy your CSV files to data/ folder
# - data/departments.csv
# - data/jobs.csv
# - data/hired_employees__1_.csv
```

### 3. Run

```bash
# Start the API server
python src/main.py
```

**Output:**
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
   - Issues found and logged to: logs/error.log

============================================================
🌐 STARTING REST API SERVER
============================================================

✅ API running at: http://localhost:5000

📋 Available Endpoints:
   Ingestion:
   - POST   /api/departments
   - POST   /api/jobs
   - POST   /api/hired_employees
...
```

---

## 📁 Project Structure

```
globant_challenge/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point - Start here!
│   ├── database.py             # Database setup & CSV loading
│   ├── validation.py           # All validation rules
│   ├── api.py                  # Flask REST API
│   ├── backup_restore.py       # AVRO backup/restore
│   └── analysis.py             # (Challenge #2) SQL queries
│
├── data/                       # CSV input files
│   ├── departments.csv
│   ├── jobs.csv
│   └── hired_employees__1_.csv
│
├── backup/                     # AVRO backup files (auto-created)
│
├── logs/                       # Error logs (auto-created)
│   └── error.log
│
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore file
├── README.md                   # This file
└── globant_challenge.db        # SQLite database (auto-created)
```

---

## 🌐 API Documentation

### Base URL
```
http://localhost:5000
```

### Health Check

**Endpoint:**
```
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "message": "API is running",
  "database": "connected"
}
```

**Test with curl:**
```bash
curl http://localhost:5000/health
```

---

### 1️⃣ Ingest Departments

**Endpoint:**
```
POST /api/departments
```

**Request Body:**
```json
{
  "data": [
    {
      "id": 1,
      "department": "Engineering"
    },
    {
      "id": 2,
      "department": "Sales"
    }
  ]
}
```

**Response (Success):**
```json
{
  "status": "success",
  "total_rows": 2,
  "inserted": 2,
  "rejected": 0,
  "errors": null
}
```

**Response (Partial - Some Invalid):**
```json
{
  "status": "partial",
  "total_rows": 3,
  "inserted": 2,
  "rejected": 1,
  "errors": [
    {
      "row_index": 2,
      "errors": ["Missing required field: department"]
    }
  ]
}
```

**Test with curl:**
```bash
curl -X POST http://localhost:5000/api/departments \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"id": 13, "department": "New Department"}
    ]
  }'
```

---

### 2️⃣ Ingest Jobs

**Endpoint:**
```
POST /api/jobs
```

**Request Body:**
```json
{
  "data": [
    {
      "id": 1,
      "job": "Software Engineer"
    },
    {
      "id": 2,
      "job": "Data Scientist"
    }
  ]
}
```

**Response:** Same format as departments endpoint

**Test with curl:**
```bash
curl -X POST http://localhost:5000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"id": 350, "job": "New Job Title"}
    ]
  }'
```

---

### 3️⃣ Ingest Hired Employees

**Endpoint:**
```
POST /api/hired_employees
```

**Request Body:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "datetime": "2021-03-15T10:30:00Z",
      "department_id": 5,
      "job_id": 42
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "datetime": "2021-06-22T14:15:00Z",
      "department_id": 3,
      "job_id": 18
    }
  ]
}
```

**Response (Success):**
```json
{
  "status": "success",
  "total_rows": 2,
  "inserted": 2,
  "rejected": 0,
  "errors": null
}
```

**Response (Validation Errors):**
```json
{
  "status": "partial",
  "total_rows": 3,
  "inserted": 2,
  "rejected": 1,
  "errors": [
    {
      "row_index": 2,
      "errors": [
        "Invalid datetime format: '2021/03/15 10:30:00' (must be ISO 8601, e.g., 2021-07-27T16:02:08Z)",
        "Department ID 999 does not exist in departments table"
      ]
    }
  ]
}
```

**Test with curl:**
```bash
curl -X POST http://localhost:5000/api/hired_employees \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "id": 10000,
        "name": "Test User",
        "datetime": "2021-05-20T09:00:00Z",
        "department_id": 5,
        "job_id": 10
      }
    ]
  }'
```

---

### Database Statistics

**Endpoint:**
```
GET /api/stats
```

**Response:**
```json
{
  "status": "success",
  "departments": 12,
  "jobs": 320,
  "hired_employees": 37500
}
```

**Test with curl:**
```bash
curl http://localhost:5000/api/stats
```

---

## ✅ Data Validation Rules

### Rule 1: All Fields Required
- `id` - Employee ID (required)
- `name` - Employee full name (required)
- `datetime` - Hire datetime (required)
- `department_id` - Department ID (required)
- `job_id` - Job ID (required)

**Example Error:**
```
"Missing required field: job_id"
```

### Rule 2: DateTime ISO 8601 Format
- **Required Format:** `YYYY-MM-DDTHH:MM:SSZ`
- **Example:** `2021-07-27T16:02:08Z`
- **UTC Timezone:** Indicated by `Z` suffix

**Valid Examples:**
- ✅ `2021-07-27T16:02:08Z`
- ✅ `2021-01-01T00:00:00Z`
- ✅ `2021-12-31T23:59:59Z`

**Invalid Examples:**
- ❌ `2021-07-27 16:02:08` (Missing T and Z)
- ❌ `2021/07/27T16:02:08Z` (Wrong date separator)
- ❌ `07-27-2021T16:02:08Z` (Wrong date format)
- ❌ `2021-07-27T16:02:08` (Missing Z)

**Example Error:**
```
"Invalid datetime format: '2021-07-27' (must be ISO 8601, e.g., 2021-07-27T16:02:08Z)"
```

### Rule 3: Department Must Exist
- `department_id` must reference an existing record in `departments` table

**Example Error:**
```
"Department ID 999 does not exist in departments table"
```

### Rule 4: Job Must Exist
- `job_id` must reference an existing record in `jobs` table

**Example Error:**
```
"Job ID 999 does not exist in jobs table"
```

### Rule 5: Invalid Records Must Be Logged
- All invalid records are logged to `logs/error.log`
- Logged in database `error_logs` table
- Error messages include timestamp and details
- Invalid records are NEVER inserted into main tables

---

## 📊 Examples

### Example 1: Single Valid Employee

**Request:**
```bash
curl -X POST http://localhost:5000/api/hired_employees \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "id": 50001,
        "name": "Alice Johnson",
        "datetime": "2021-09-15T14:30:00Z",
        "department_id": 5,
        "job_id": 100
      }
    ]
  }'
```

**Response:**
```json
{
  "status": "success",
  "total_rows": 1,
  "inserted": 1,
  "rejected": 0,
  "errors": null
}
```

---

### Example 2: Batch with Mixed Valid/Invalid Records

**Request:**
```bash
curl -X POST http://localhost:5000/api/hired_employees \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "id": 50002,
        "name": "Bob Smith",
        "datetime": "2021-03-20T10:00:00Z",
        "department_id": 2,
        "job_id": 45
      },
      {
        "id": 50003,
        "name": "Carol White",
        "datetime": "INVALID-DATE",
        "department_id": 2,
        "job_id": 45
      },
      {
        "id": 50004,
        "name": "David Lee",
        "datetime": "2021-06-10T08:30:00Z",
        "department_id": 9999,
        "job_id": 50
      }
    ]
  }'
```

**Response:**
```json
{
  "status": "partial",
  "total_rows": 3,
  "inserted": 1,
  "rejected": 2,
  "errors": [
    {
      "row_index": 1,
      "errors": [
        "Invalid datetime format: 'INVALID-DATE' (must be ISO 8601, e.g., 2021-07-27T16:02:08Z)"
      ]
    },
    {
      "row_index": 2,
      "errors": [
        "Department ID 9999 does not exist in departments table"
      ]
    }
  ]
}
```

**Logs (in logs/error.log):**
```
2024-01-15 10:45:30 | hired_employees | ID: 50003 | Invalid datetime format: 'INVALID-DATE' (must be ISO 8601, e.g., 2021-07-27T16:02:08Z)
2024-01-15 10:45:30 | hired_employees | ID: 50004 | Department ID 9999 does not exist in departments table
```

---

### Example 3: Batch Size Limit

**Request (> 1000 rows):**
```bash
curl -X POST http://localhost:5000/api/hired_employees \
  -H "Content-Type: application/json" \
  -d '{
    "data": [... 1001 records ...]
  }'
```

**Response:**
```json
{
  "status": "error",
  "message": "Batch size cannot exceed 1000 records"
}
```

---

## 🔄 Backup & Restore

### Backup Table

**Endpoint:**
```
GET /api/backup?table=hired_employees
```

**Query Parameters:**
- `table` (required): Table name (departments, jobs, or hired_employees)

**Response:**
```json
{
  "status": "success",
  "filename": "backup/hired_employees_20240115_104530.avro",
  "rows_backed_up": 37500,
  "timestamp": "20240115_104530"
}
```

**Test with curl:**
```bash
curl "http://localhost:5000/api/backup?table=hired_employees"
```

**Files Created:**
```
backup/
  ├── hired_employees_20240115_104530.avro
  ├── departments_20240115_104535.avro
  └── jobs_20240115_104540.avro
```

---

### Restore Table

**Endpoint:**
```
POST /api/restore
```

**Request Body:**
```json
{
  "filename": "backup/hired_employees_20240115_104530.avro"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Restored 37500 rows to hired_employees",
  "rows_restored": 37500,
  "table": "hired_employees"
}
```

**Test with curl:**
```bash
curl -X POST http://localhost:5000/api/restore \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "backup/hired_employees_20240115_104530.avro"
  }'
```

**Process:**
1. Read AVRO file
2. Clear existing table data
3. Insert all records from backup
4. Commit transaction

---

## 🏗️ Architecture & Design Decisions

### 1. **Separate Endpoints Per Table**

**Decision:** Use separate endpoints (`/api/departments`, `/api/jobs`, `/api/hired_employees`)

**Why?**
- ✅ **Clarity**: Each endpoint has clear purpose
- ✅ **Maintainability**: Easier to modify individual table logic
- ✅ **Scalability**: Different validation rules per table
- ✅ **REST Best Practice**: Follows RESTful conventions
- ✅ **Error Handling**: Specific error messages per table

**Alternative (Not Chosen): Generic Endpoint**
```
POST /api/ingest?table=hired_employees
```
❌ More complex parameter handling
❌ Harder to maintain
❌ Violates REST conventions

---

### 2. **Validation Module (Centralized)**

**Decision:** Single validation module with reusable functions

**Why?**
- ✅ **DRY Principle**: No code duplication
- ✅ **Consistency**: All tables validated same way
- ✅ **Testability**: Easy to unit test
- ✅ **Maintainability**: Update rules in one place

**Structure:**
```python
validation.py
├── is_iso_datetime()          # Rule 2
├── department_exists()        # Rule 3
├── job_exists()               # Rule 4
├── validate_hired_employee()  # All rules
├── validate_department()
├── validate_job()
└── log_error()                # Rule 5
```

---

### 3. **SQLite Database (Not PostgreSQL/MySQL)**

**Decision:** Use SQLite for simplicity

**Why?**
- ✅ **No Setup Required**: File-based, zero configuration
- ✅ **Development Speed**: Can test immediately
- ✅ **Portability**: Single .db file, easy to share
- ✅ **Sufficient**: Perfect for PoC and testing
- ✅ **ACID Compliance**: Transactions work perfectly

**For Production:** Migration to PostgreSQL is straightforward

---

### 4. **Flask (Not FastAPI)**

**Decision:** Use Flask for REST API

**Why?**
- ✅ **Simple**: Less boilerplate than FastAPI
- ✅ **Lightweight**: Quick to get running
- ✅ **Learning Curve**: Easier to understand
- ✅ **Sufficient**: Handles all requirements
- ✅ **Proven**: Battle-tested in production

**For High Performance:** FastAPI would be better for async operations

---

### 5. **Batch Ingestion (1-1000 rows)**

**Decision:** Support batch sizes with maximum of 1000 records

**Why?**
- ✅ **Performance**: Process multiple records in one request
- ✅ **Network Efficiency**: Reduce HTTP overhead
- ✅ **Safety**: Prevent memory overload (1000 record limit)
- ✅ **Flexibility**: Support single record (batch=1) to full batch (batch=1000)

**Implementation:**
```python
if len(data) > 1000:
    return error("Batch size cannot exceed 1000 records")
```

---

### 6. **AVRO for Backups**

**Decision:** Use Apache AVRO format for backups

**Why?**
- ✅ **Schema Evolution**: Supports schema changes
- ✅ **Compression**: Efficient storage
- ✅ **Type Safety**: Enforces schema
- ✅ **Industry Standard**: Used in data engineering
- ✅ **Interoperability**: Works across languages/tools

---

### 7. **Logging Strategy**

**Dual Logging:**
1. **File Logging** (`logs/error.log`): Human-readable, searchable
2. **Database Logging** (`error_logs` table): Queryable, reportable

**Format:**
```
TIMESTAMP | TABLE | ID | ERROR_DETAILS
```

**Example:**
```
2024-01-15 10:45:30 | hired_employees | 50003 | Invalid datetime format: 'INVALID-DATE'
```

---

## 🔧 Troubleshooting

### Problem: "Port 5000 already in use"

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use a different port
python src/main.py --port 5001
```

---

### Problem: "No such file: globant_challenge.db"

**Solution:**
The database is created automatically on first run. Ensure you're in the correct directory:
```bash
cd /path/to/globant_challenge
python src/main.py
```

---

### Problem: "ImportError: No module named 'fastavro'"

**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Or install specific package
pip install fastavro==1.8.0
```

---

### Problem: "CSV file not found"

**Solution:**
1. Ensure CSV files are in `data/` folder:
   ```bash
   ls data/
   # Should show:
   # departments.csv
   # jobs.csv
   # hired_employees__1_.csv
   ```

2. If using different filenames, update `load_historical_data()` in `database.py`

---

### Problem: "Foreign key constraint failed"

**Solution:**
This happens when inserting employee with non-existent department/job.

The API already handles this with validation. Check:
1. Validation logged the error: `cat logs/error.log`
2. Database integrity: `sqlite3 globant_challenge.db "SELECT * FROM departments LIMIT 5"`

---

### Problem: "API returns 500 error"

**Solution:**
1. Check logs: `tail -f logs/error.log`
2. Check console output for traceback
3. Verify request format matches documentation
4. Test with curl first: `curl http://localhost:5000/health`

---

## 📝 API Response Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | All records inserted |
| 200 | Partial Success | Some records inserted, some rejected |
| 400 | Bad Request | Invalid JSON, missing required fields |
| 404 | Not Found | Endpoint doesn't exist |
| 500 | Server Error | Database error, file error |

---

## 🔐 Security Considerations

### Input Validation
- ✅ All inputs validated before database insertion
- ✅ Type checking on numeric fields
- ✅ Length validation on string fields

### SQL Injection Prevention
- ✅ Using parameterized queries (?) throughout
- ✅ Never concatenating user input into SQL

### Error Handling
- ✅ Detailed error messages for validation failures
- ✅ No sensitive information leaked in API responses
- ✅ All errors logged to file for debugging

### Production Recommendations
- 🔐 Add authentication (JWT or OAuth2)
- 🔐 Add rate limiting to prevent abuse
- 🔐 Use HTTPS/TLS encryption
- 🔐 Add request size limits
- 🔐 Implement audit logging

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Apache AVRO](https://avro.apache.org/)
- [Python Datetime ISO Format](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)

---

## 📞 Support

If you encounter issues:

1. **Check logs**: `tail logs/error.log`
2. **Test endpoint**: `curl http://localhost:5000/health`
3. **Verify database**: `sqlite3 globant_challenge.db ".tables"`
4. **Read error messages**: API responses include detailed error information

---

**Built with ❤️ for the Globant Data Engineer Challenge**

Version 1.0 | January 2024
