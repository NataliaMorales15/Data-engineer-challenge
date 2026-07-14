"""
Database Module - SQLite Setup and Data Loading
Handles database connection, schema creation, and CSV ingestion
"""

import sqlite3
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename='logs/error.log',
    level=logging.ERROR,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = 'globant_challenge.db'

def get_connection():
    """
    Get SQLite database connection
    
    Returns:
        sqlite3.Connection: Database connection with Row factory
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_database():
    """
    Initialize database and create schema
    
    Creates three tables:
    - departments: id (PK), department (name)
    - jobs: id (PK), job (name)
    - hired_employees: id (PK), name, datetime, department_id (FK), job_id (FK)
    - error_logs: For tracking validation errors
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Create departments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                department VARCHAR(255) NOT NULL UNIQUE
            )
        ''')
        
        # Create jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY,
                job VARCHAR(255) NOT NULL UNIQUE
            )
        ''')
        
        # Create hired_employees table
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
        
        # Create error_logs table for tracking validation failures
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name VARCHAR(255),
                record_id INTEGER,
                errors TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_he_datetime ON hired_employees(datetime)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_he_department_id ON hired_employees(department_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_he_job_id ON hired_employees(job_id)')
        
        conn.commit()
        logger.info("Database schema created successfully")
        
    except sqlite3.Error as e:
        logger.error(f"Error creating database schema: {e}")
        raise
    finally:
        conn.close()

def load_historical_data(csv_folder='data'):
    """
    Load CSV files into database
    
    This is raw data loading WITHOUT validation.
    Validation happens during API ingestion.
    
    Args:
        csv_folder (str): Path to folder containing CSV files
        
    Returns:
        dict: Statistics of loaded records
    """
    conn = get_connection()
    stats = {}
    
    try:
        # Load departments.csv
        try:
            df_dept = pd.read_csv(
                f'{csv_folder}/departments.csv',
                header=None,
                names=['id', 'department']
            )
            # Clear existing data first
            conn.execute('DELETE FROM departments')
            df_dept.to_sql('departments', conn, if_exists='append', index=False)
            stats['departments'] = len(df_dept)
            logger.info(f"Loaded {len(df_dept)} departments")
        except FileNotFoundError:
            logger.warning(f"departments.csv not found in {csv_folder}")
            stats['departments'] = 0
        
        # Load jobs.csv
        try:
            df_jobs = pd.read_csv(
                f'{csv_folder}/jobs.csv',
                header=None,
                names=['id', 'job']
            )
            # Clear existing data first
            conn.execute('DELETE FROM jobs')
            df_jobs.to_sql('jobs', conn, if_exists='append', index=False)
            stats['jobs'] = len(df_jobs)
            logger.info(f"Loaded {len(df_jobs)} jobs")
        except FileNotFoundError:
            logger.warning(f"jobs.csv not found in {csv_folder}")
            stats['jobs'] = 0
        
        # Load hired_employees.csv (this will have validation issues)
        try:
            df_hired = pd.read_csv(
                f'{csv_folder}/hired_employees__1_.csv',
                header=None,
                names=['id', 'name', 'datetime', 'department_id', 'job_id']
            )
            # Clear existing data first
            conn.execute('DELETE FROM hired_employees')
            df_hired.to_sql('hired_employees', conn, if_exists='append', index=False)
            stats['hired_employees'] = len(df_hired)
            logger.info(f"Loaded {len(df_hired)} hired_employees (raw data with potential issues)")
        except FileNotFoundError:
            logger.warning(f"hired_employees__1_.csv not found in {csv_folder}")
            stats['hired_employees'] = 0
        
        conn.commit()
        return stats
        
    except Exception as e:
        logger.error(f"Error loading CSV data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def check_data_quality():
    """
    Check data quality and identify invalid records
    
    Returns:
        dict: Quality statistics
    """
    conn = get_connection()
    cursor = conn.cursor()
    report = {}
    
    try:
        # Count total records
        cursor.execute('SELECT COUNT(*) FROM hired_employees')
        total = cursor.fetchone()[0]
        
        # Count records with missing fields
        cursor.execute('''
            SELECT COUNT(*) FROM hired_employees
            WHERE id IS NULL OR name IS NULL OR datetime IS NULL 
               OR department_id IS NULL OR job_id IS NULL
        ''')
        missing_fields = cursor.fetchone()[0]
        
        # Count records with invalid datetime format
        invalid_datetime = 0
        cursor.execute('SELECT id, datetime FROM hired_employees')
        for row in cursor.fetchall():
            if not is_iso_datetime(row[1]):
                invalid_datetime += 1
        
        # Count records with non-existent department
        cursor.execute('''
            SELECT COUNT(*) FROM hired_employees he
            LEFT JOIN departments d ON he.department_id = d.id
            WHERE d.id IS NULL
        ''')
        invalid_dept = cursor.fetchone()[0]
        
        # Count records with non-existent job
        cursor.execute('''
            SELECT COUNT(*) FROM hired_employees he
            LEFT JOIN jobs j ON he.job_id = j.id
            WHERE j.id IS NULL
        ''')
        invalid_job = cursor.fetchone()[0]
        
        # Calculate valid records
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
    """
    Validate ISO 8601 datetime format
    
    Expected format: 2021-07-27T16:02:08Z
    
    Args:
        date_string: String to validate
        
    Returns:
        bool: True if valid ISO datetime, False otherwise
    """
    if not date_string:
        return False
    
    try:
        # Try parsing ISO format with Z at end
        if isinstance(date_string, str):
            datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return True
        return False
    except (ValueError, AttributeError, TypeError):
        return False

def table_exists(table_name):
    """
    Check if table exists in database
    
    Args:
        table_name (str): Name of table to check
        
    Returns:
        bool: True if table exists
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        exists = cursor.fetchone() is not None
        return exists
    finally:
        conn.close()

def get_table_count(table_name):
    """
    Get record count for a table
    
    Args:
        table_name (str): Name of table
        
    Returns:
        int: Number of records
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        return count
    finally:
        conn.close()

if __name__ == '__main__':
    # For testing
    init_database()
    stats = load_historical_data()
    print("Data loading stats:", stats)
