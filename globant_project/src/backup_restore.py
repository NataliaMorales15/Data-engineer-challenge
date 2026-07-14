"""
Backup & Restore Module - AVRO Format
Handles export/import of tables in AVRO format
"""

import fastavro
import logging
import os
from datetime import datetime
from database import get_connection

# Setup logging
logging.basicConfig(
    filename='logs/error.log',
    level=logging.ERROR,
    format='%(asctime)s | %(message)s'
)
logger = logging.getLogger(__name__)

BACKUP_DIR = 'backup'

def ensure_backup_dir():
    """Create backup directory if it doesn't exist"""
    os.makedirs(BACKUP_DIR, exist_ok=True)

def get_table_schema(table_name):
    """
    Get AVRO schema for a table
    
    Args:
        table_name (str): Name of table
        
    Returns:
        dict: AVRO schema definition
    """
    schemas = {
        'departments': {
            'type': 'record',
            'name': 'departments',
            'fields': [
                {'name': 'id', 'type': 'int'},
                {'name': 'department', 'type': 'string'}
            ]
        },
        'jobs': {
            'type': 'record',
            'name': 'jobs',
            'fields': [
                {'name': 'id', 'type': 'int'},
                {'name': 'job', 'type': 'string'}
            ]
        },
        'hired_employees': {
            'type': 'record',
            'name': 'hired_employees',
            'fields': [
                {'name': 'id', 'type': 'int'},
                {'name': 'name', 'type': 'string'},
                {'name': 'datetime', 'type': 'string'},
                {'name': 'department_id', 'type': 'int'},
                {'name': 'job_id', 'type': 'int'}
            ]
        }
    }
    
    if table_name not in schemas:
        raise ValueError(f"Unknown table: {table_name}")
    
    return schemas[table_name]

def backup_table(table_name, db_path='globant_challenge.db'):
    """
    Backup a table to AVRO format
    
    Args:
        table_name (str): Name of table to backup
        db_path (str): Path to database file
        
    Returns:
        dict: Backup info {filename, rows, timestamp} or None on error
    """
    ensure_backup_dir()
    
    try:
        conn = get_connection()
        conn.row_factory = None  # Reset row factory to get tuples
        cursor = conn.cursor()
        
        # Get table data
        cursor.execute(f'SELECT * FROM {table_name}')
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f'PRAGMA table_info({table_name})')
        columns = [row[1] for row in cursor.fetchall()]
        
        # Convert tuples to dicts
        data = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        
        if not data:
            logger.warning(f"No data to backup from {table_name}")
            return None
        
        # Get schema
        schema = get_table_schema(table_name)
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{BACKUP_DIR}/{table_name}_{timestamp}.avro'
        
        # Write AVRO file
        with open(filename, 'wb') as f:
            fastavro.writer(f, schema, data)
        
        logger.info(f"Backed up {table_name}: {len(data)} rows to {filename}")
        
        return {
            'filename': filename,
            'rows': len(data),
            'timestamp': timestamp,
            'table': table_name
        }
        
    except Exception as e:
        logger.error(f"Backup failed for {table_name}: {e}")
        return None

def restore_table(filename, db_path='globant_challenge.db'):
    """
    Restore a table from AVRO backup
    
    Args:
        filename (str): Path to AVRO backup file
        db_path (str): Path to database file
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if not os.path.exists(filename):
            return False, f"File not found: {filename}"
        
        # Read AVRO file
        with open(filename, 'rb') as f:
            reader = fastavro.reader(f)
            records = list(reader)
        
        if not records:
            return False, "No data in backup file"
        
        # Get table name from filename
        table_name = os.path.basename(filename).split('_')[0]
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Delete existing data
        cursor.execute(f'DELETE FROM {table_name}')
        
        # Insert records
        first_record = records[0]
        columns = list(first_record.keys())
        placeholders = ','.join(['?' for _ in columns])
        column_names = ','.join(columns)
        
        for record in records:
            values = [record.get(col) for col in columns]
            cursor.execute(
                f'INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})',
                values
            )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Restored {len(records)} rows to {table_name} from {filename}")
        return True, f"Restored {len(records)} rows to {table_name}"
        
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        return False, str(e)

def list_backups():
    """
    List all available backups
    
    Returns:
        list: List of backup files
    """
    ensure_backup_dir()
    
    try:
        files = []
        for file in sorted(os.listdir(BACKUP_DIR)):
            if file.endswith('.avro'):
                filepath = os.path.join(BACKUP_DIR, file)
                size = os.path.getsize(filepath)
                files.append({
                    'filename': file,
                    'path': filepath,
                    'size': size
                })
        return sorted(files, key=lambda x: x['filename'], reverse=True)
    except Exception as e:
        logger.error(f"Failed to list backups: {e}")
        return []

# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    # Test backup
    print("Testing backup functionality...")
    
    ensure_backup_dir()
    
    # Backup departments
    result = backup_table('departments')
    if result:
        print(f"✅ Backed up departments: {result}")
    else:
        print("❌ Failed to backup departments")
    
    # Backup jobs
    result = backup_table('jobs')
    if result:
        print(f"✅ Backed up jobs: {result}")
    else:
        print("❌ Failed to backup jobs")
    
    # Backup hired_employees
    result = backup_table('hired_employees')
    if result:
        print(f"✅ Backed up hired_employees: {result}")
    else:
        print("❌ Failed to backup hired_employees")
    
    # List backups
    print("\nAvailable backups:")
    for backup in list_backups():
        print(f"  - {backup['filename']} ({backup['size']} bytes)")
