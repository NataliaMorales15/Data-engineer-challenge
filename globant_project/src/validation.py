"""
Validation Module - Data Validation Rules
Implements all 5 validation rules for the challenge
"""

from datetime import datetime
import sqlite3
import logging

# Setup logging
logging.basicConfig(
    filename='logs/error.log',
    level=logging.ERROR,
    format='%(asctime)s | %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# VALIDATION RULE FUNCTIONS
# ============================================================================

def is_iso_datetime(date_string):
    """
    RULE 2: Validate ISO 8601 datetime format
    
    Expected format: 2021-07-27T16:02:08Z
    
    Args:
        date_string: String to validate
        
    Returns:
        bool: True if valid ISO datetime
    """
    if not date_string or date_string == '':
        return False
    
    try:
        if isinstance(date_string, str):
            # Parse ISO format with Z at end (UTC)
            datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return True
        return False
    except (ValueError, AttributeError, TypeError):
        return False

def department_exists(dept_id, conn):
    """
    RULE 3: Check if department exists in database
    
    Args:
        dept_id: Department ID to check
        conn: Database connection
        
    Returns:
        bool: True if department exists
    """
    if not dept_id or dept_id == '':
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM departments WHERE id = ?', (int(dept_id),))
        return cursor.fetchone() is not None
    except (ValueError, TypeError):
        return False

def job_exists(job_id, conn):
    """
    RULE 4: Check if job exists in database
    
    Args:
        job_id: Job ID to check
        conn: Database connection
        
    Returns:
        bool: True if job exists
    """
    if not job_id or job_id == '':
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM jobs WHERE id = ?', (int(job_id),))
        return cursor.fetchone() is not None
    except (ValueError, TypeError):
        return False

# ============================================================================
# MAIN VALIDATION FUNCTIONS FOR EACH TABLE
# ============================================================================

def validate_hired_employee(row, conn):
    """
    Validate a hired employee record against all rules
    
    Rules:
    1. All fields required (id, name, datetime, department_id, job_id)
    2. datetime must be ISO 8601 format
    3. department_id must exist in departments table
    4. job_id must exist in jobs table
    
    Args:
        row (dict): Record to validate
        conn: Database connection
        
    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    errors = []
    
    # RULE 1: All fields required
    if not row.get('id') or row['id'] == '':
        errors.append("Missing required field: id")
    
    if not row.get('name') or row['name'] == '':
        errors.append("Missing required field: name")
    
    if not row.get('datetime') or row['datetime'] == '':
        errors.append("Missing required field: datetime")
    
    if row.get('department_id') is None or row['department_id'] == '':
        errors.append("Missing required field: department_id")
    
    if row.get('job_id') is None or row['job_id'] == '':
        errors.append("Missing required field: job_id")
    
    # If we already have missing field errors, no point checking further
    if errors:
        log_error('hired_employees', row.get('id', 'UNKNOWN'), errors)
        return False, errors
    
    # RULE 2: Validate datetime format (ISO 8601)
    if not is_iso_datetime(row['datetime']):
        errors.append(f"Invalid datetime format: '{row['datetime']}' (must be ISO 8601, e.g., 2021-07-27T16:02:08Z)")
    
    # RULE 3: Validate department exists
    if not department_exists(row['department_id'], conn):
        errors.append(f"Department ID {row['department_id']} does not exist in departments table")
    
    # RULE 4: Validate job exists
    if not job_exists(row['job_id'], conn):
        errors.append(f"Job ID {row['job_id']} does not exist in jobs table")
    
    # Log errors if any
    if errors:
        log_error('hired_employees', row.get('id'), errors)
        return False, errors
    
    return True, []

def validate_department(row, conn):
    """
    Validate a department record
    
    Rules:
    - id and department fields required
    
    Args:
        row (dict): Record to validate
        conn: Database connection
        
    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    errors = []
    
    if not row.get('id') or row['id'] == '':
        errors.append("Missing required field: id")
    
    if not row.get('department') or row['department'] == '':
        errors.append("Missing required field: department")
    
    if errors:
        log_error('departments', row.get('id', 'UNKNOWN'), errors)
        return False, errors
    
    return True, []

def validate_job(row, conn):
    """
    Validate a job record
    
    Rules:
    - id and job fields required
    
    Args:
        row (dict): Record to validate
        conn: Database connection
        
    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    errors = []
    
    if not row.get('id') or row['id'] == '':
        errors.append("Missing required field: id")
    
    if not row.get('job') or row['job'] == '':
        errors.append("Missing required field: job")
    
    if errors:
        log_error('jobs', row.get('id', 'UNKNOWN'), errors)
        return False, errors
    
    return True, []

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

def log_error(table_name, record_id, errors):
    """
    Log validation errors to file and error_logs table
    
    RULE 5: Invalid records MUST be logged
    
    Args:
        table_name (str): Name of table
        record_id: ID of invalid record
        errors (list): List of error messages
    """
    error_message = ' | '.join(errors)
    log_entry = f"{table_name} | ID: {record_id} | {error_message}"
    
    # Log to console
    print(f"⚠️  {log_entry}")
    
    # Log to file
    logger.error(log_entry)
    
    # Optionally: Log to database
    try:
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO error_logs (table_name, record_id, errors) VALUES (?, ?, ?)',
            (table_name, record_id, error_message)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log error to database: {e}")

def get_validation_errors(limit=100):
    """
    Retrieve logged validation errors
    
    Args:
        limit (int): Maximum number of errors to retrieve
        
    Returns:
        list: List of error log records
    """
    try:
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT timestamp, table_name, record_id, errors FROM error_logs ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        errors = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return errors
    except Exception as e:
        logger.error(f"Failed to retrieve errors: {e}")
        return []

# ============================================================================
# BATCH VALIDATION
# ============================================================================

def validate_batch(records, table_name, conn):
    """
    Validate a batch of records
    
    Args:
        records (list): List of records to validate
        table_name (str): Name of table (hired_employees, departments, or jobs)
        conn: Database connection
        
    Returns:
        dict: {
            'valid': [valid records],
            'invalid': [{'row_index': int, 'record': dict, 'errors': list}],
            'stats': {'total': int, 'valid': int, 'invalid': int}
        }
    """
    valid_records = []
    invalid_records = []
    
    # Choose validation function based on table name
    if table_name == 'hired_employees':
        validator = validate_hired_employee
    elif table_name == 'departments':
        validator = validate_department
    elif table_name == 'jobs':
        validator = validate_job
    else:
        raise ValueError(f"Unknown table: {table_name}")
    
    # Validate each record
    for idx, record in enumerate(records):
        is_valid, errors = validator(record, conn)
        
        if is_valid:
            valid_records.append(record)
        else:
            invalid_records.append({
                'row_index': idx,
                'record': record,
                'errors': errors
            })
    
    return {
        'valid': valid_records,
        'invalid': invalid_records,
        'stats': {
            'total': len(records),
            'valid': len(valid_records),
            'invalid': len(invalid_records)
        }
    }

# ============================================================================
# TESTING / DEBUG
# ============================================================================

if __name__ == '__main__':
    # Test validation functions
    from database import get_connection, init_database
    
    init_database()
    conn = get_connection()
    
    # Test valid record
    valid_record = {
        'id': 9999,
        'name': 'Test User',
        'datetime': '2021-03-15T10:30:00Z',
        'department_id': 1,
        'job_id': 1
    }
    
    is_valid, errors = validate_hired_employee(valid_record, conn)
    print(f"Valid record test: {is_valid} (errors: {errors})")
    
    # Test invalid record (missing job_id)
    invalid_record = {
        'id': 9998,
        'name': 'Test User',
        'datetime': '2021-03-15T10:30:00Z',
        'department_id': 1,
        'job_id': None
    }
    
    is_valid, errors = validate_hired_employee(invalid_record, conn)
    print(f"Invalid record test: {is_valid} (errors: {errors})")
    
    conn.close()
