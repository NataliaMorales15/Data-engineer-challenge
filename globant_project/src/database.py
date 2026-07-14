"""
Database Module - SQLite Setup and Data Loading
Handles database connection, schema creation, and CSV ingestion
"""
 
import sqlite3
import csv
import logging
from datetime import datetime
import os
 
# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/error.log',
    level=logging.ERROR,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)
 
# Database configuration
DB_PATH = 'globant_challenge.db'
 
 
def get_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
 
 
def init_database():
    """Initialize database and create schema"""
    conn = get_connection()
    cursor = conn.cursor()
 
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                department VARCHAR(255) NOT NULL UNIQUE
            )
        ''')
 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY,
                job VARCHAR(255) NOT NULL UNIQUE
            )
        ''')
 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hired_employees (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                datetime TEXT NOT NULL,
                department_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                FOREIGN KEY (department_id) REFERENCES departments(id),
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        ''')
 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name VARCHAR(255),
                record_id INTEGER,
                errors TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
 
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_he_datetime ON hired_employees(datetime)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_he_department_id ON hired_employees(department_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_he_job_id ON hired_employees(job_id)')
 
        conn.commit()
 
    except sqlite3.Error as e:
        logger.error(f"Error creating database schema: {e}")
        raise
    finally:
        conn.close()
 
 
def load_historical_data(csv_folder='data'):
    """Load CSV files into database using built-in csv module"""
    conn = get_connection()
    stats = {}
 
    try:
        # Load departments.csv
        try:
            with open(f'{csv_folder}/departments.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                conn.execute('DELETE FROM departments')
                count = 0
                for row in reader:
                    try:
                        if len(row) >= 2 and row[0].strip() and row[1].strip():
                            conn.execute(
                                'INSERT OR REPLACE INTO departments (id, department) VALUES (?, ?)',
                                (int(row[0].strip()), row[1].strip())
                            )
                            count += 1
                    except Exception:
                        pass
                conn.commit()
            stats['departments'] = count
        except FileNotFoundError:
            stats['departments'] = 0
 
        # Load jobs.csv
        try:
            with open(f'{csv_folder}/jobs.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                conn.execute('DELETE FROM jobs')
                count = 0
                for row in reader:
                    try:
                        if len(row) >= 2 and row[0].strip() and row[1].strip():
                            conn.execute(
                                'INSERT OR REPLACE INTO jobs (id, job) VALUES (?, ?)',
                                (int(row[0].strip()), row[1].strip())
                            )
                            count += 1
                    except Exception:
                        pass
                conn.commit()
            stats['jobs'] = count
        except FileNotFoundError:
            stats['jobs'] = 0
 
        # Load hired_employees.csv
        try:
            with open(f'{csv_folder}/hired_employees.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                conn.execute('DELETE FROM hired_employees')
                count = 0
                for row in reader:
                    try:
                        if len(row) >= 5:
                            id_val = row[0].strip() if row[0] else ''
                            name = row[1].strip() if row[1] else ''
                            dt = row[2].strip() if row[2] else ''
                            dept_id = row[3].strip() if row[3] else ''
                            job_id = row[4].strip() if row[4] else ''
 
                            if id_val and name and dt and dept_id and job_id:
                                conn.execute(
                                    'INSERT INTO hired_employees (id, name, datetime, department_id, job_id) VALUES (?, ?, ?, ?, ?)',
                                    (int(id_val), name, dt, int(dept_id), int(job_id))
                                )
                                count += 1
                    except Exception:
                        pass
                conn.commit()
            stats['hired_employees'] = count
        except FileNotFoundError:
            stats['hired_employees'] = 0
 
        return stats
 
    except Exception as e:
        logger.error(f"Error loading CSV data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
 
 
def check_data_quality():
    """Check data quality and identify invalid records"""
    conn = get_connection()
    cursor = conn.cursor()
    report = {}
 
    try:
        cursor.execute('SELECT COUNT(*) FROM hired_employees')
        total = cursor.fetchone()[0]
 
        cursor.execute('''
            SELECT COUNT(*) FROM hired_employees
            WHERE id IS NULL OR name IS NULL OR datetime IS NULL
               OR department_id IS NULL OR job_id IS NULL
        ''')
        missing_fields = cursor.fetchone()[0]
 
        invalid_datetime = 0
        cursor.execute('SELECT id, datetime FROM hired_employees')
        for row in cursor.fetchall():
            if not is_iso_datetime(row[1]):
                invalid_datetime += 1
 
        cursor.execute('''
            SELECT COUNT(*) FROM hired_employees he
            LEFT JOIN departments d ON he.department_id = d.id
            WHERE d.id IS NULL
        ''')
        invalid_dept = cursor.fetchone()[0]
 
        cursor.execute('''
            SELECT COUNT(*) FROM hired_employees he
            LEFT JOIN jobs j ON he.job_id = j.id
            WHERE j.id IS NULL
        ''')
        invalid_job = cursor.fetchone()[0]
 
        invalid_total = missing_fields + invalid_datetime + invalid_dept + invalid_job
        valid = total - invalid_total
 
        report['total_records'] = total
        report['valid_employees'] = max(0, valid)
        report['invalid_employees'] = min(invalid_total, total)
        report['missing_fields'] = missing_fields
        report['invalid_datetime'] = invalid_datetime
        report['invalid_department'] = invalid_dept
        report['invalid_job'] = invalid_job
 
        return report
 
    except Exception as e:
        logger.error(f"Error checking data quality: {e}")
        return {'error': str(e)}
    finally:
        conn.close()
 
 
def is_iso_datetime(date_string):
    """Validate ISO 8601 datetime format"""
    if not date_string:
        return False
    try:
        if isinstance(date_string, str):
            datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return True
        return False
    except (ValueError, AttributeError, TypeError):
        return False
 
 
def table_exists(table_name):
    """Check if table exists in database"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        exists = cursor.fetchone() is not None
        return exists
    finally:
        conn.close()
 
 
def get_table_count(table_name):
    """Get record count for a table"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        return count
    finally:
        conn.close()
 
 
if __name__ == '__main__':
    init_database()
    stats = load_historical_data()
    print("Data loading stats:", stats)