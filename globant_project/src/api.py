"""
REST API Module - Flask Application
Handles all API endpoints for data ingestion, analysis, backup and restore
"""
 
from flask import Flask, request, jsonify
from database import get_connection, get_table_count
from validation import validate_batch
from backup_restore import backup_table, restore_table, list_backups
import logging
import os
 
# Initialize Flask app
app = Flask(__name__)
 
# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/error.log',
    level=logging.ERROR,
    format='%(asctime)s | %(message)s'
)
logger = logging.getLogger(__name__)
 
 
# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================
 
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'API is running',
        'database': 'connected'
    }), 200
 
 
@app.route('/api/stats', methods=['GET'])
def stats():
    """Get database statistics"""
    try:
        return jsonify({
            'status': 'success',
            'departments': get_table_count('departments'),
            'jobs': get_table_count('jobs'),
            'hired_employees': get_table_count('hired_employees')
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
 
 
# ============================================================================
# DATA INGESTION ENDPOINTS
# ============================================================================
 
@app.route('/api/departments', methods=['POST'])
def ingest_departments():
    """Ingest departments - batch 1 to 1000 rows"""
    try:
        data = request.json.get('data', [])
 
        if not isinstance(data, list):
            return jsonify({'status': 'error', 'message': 'Data must be a list'}), 400
 
        if len(data) > 1000:
            return jsonify({'status': 'error', 'message': 'Batch size cannot exceed 1000 records'}), 400
 
        if len(data) == 0:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
 
        conn = get_connection()
        validation_result = validate_batch(data, 'departments', conn)
 
        cursor = conn.cursor()
        for record in validation_result['valid']:
            try:
                cursor.execute(
                    'INSERT OR REPLACE INTO departments (id, department) VALUES (?, ?)',
                    (record['id'], record['department'])
                )
            except Exception as e:
                logger.error(f"departments | ID: {record.get('id')} | Database error: {str(e)}")
 
        conn.commit()
        conn.close()
 
        response = {
            'status': 'success' if validation_result['stats']['invalid'] == 0 else 'partial',
            'total_rows': validation_result['stats']['total'],
            'inserted': validation_result['stats']['valid'],
            'rejected': validation_result['stats']['invalid'],
            'errors': None
        }
 
        if validation_result['invalid']:
            response['errors'] = [
                {'row_index': err['row_index'], 'errors': err['errors']}
                for err in validation_result['invalid']
            ]
 
        return jsonify(response), 200
 
    except Exception as e:
        logger.error(f"departments endpoint error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
 
 
@app.route('/api/jobs', methods=['POST'])
def ingest_jobs():
    """Ingest jobs - batch 1 to 1000 rows"""
    try:
        data = request.json.get('data', [])
 
        if not isinstance(data, list):
            return jsonify({'status': 'error', 'message': 'Data must be a list'}), 400
 
        if len(data) > 1000:
            return jsonify({'status': 'error', 'message': 'Batch size cannot exceed 1000 records'}), 400
 
        if len(data) == 0:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
 
        conn = get_connection()
        validation_result = validate_batch(data, 'jobs', conn)
 
        cursor = conn.cursor()
        for record in validation_result['valid']:
            try:
                cursor.execute(
                    'INSERT OR REPLACE INTO jobs (id, job) VALUES (?, ?)',
                    (record['id'], record['job'])
                )
            except Exception as e:
                logger.error(f"jobs | ID: {record.get('id')} | Database error: {str(e)}")
 
        conn.commit()
        conn.close()
 
        response = {
            'status': 'success' if validation_result['stats']['invalid'] == 0 else 'partial',
            'total_rows': validation_result['stats']['total'],
            'inserted': validation_result['stats']['valid'],
            'rejected': validation_result['stats']['invalid'],
            'errors': None
        }
 
        if validation_result['invalid']:
            response['errors'] = [
                {'row_index': err['row_index'], 'errors': err['errors']}
                for err in validation_result['invalid']
            ]
 
        return jsonify(response), 200
 
    except Exception as e:
        logger.error(f"jobs endpoint error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
 
 
@app.route('/api/hired_employees', methods=['POST'])
def ingest_hired_employees():
    """Ingest hired employees - batch 1 to 1000 rows"""
    try:
        data = request.json.get('data', [])
 
        if not isinstance(data, list):
            return jsonify({'status': 'error', 'message': 'Data must be a list'}), 400
 
        if len(data) > 1000:
            return jsonify({'status': 'error', 'message': 'Batch size cannot exceed 1000 records'}), 400
 
        if len(data) == 0:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
 
        conn = get_connection()
        validation_result = validate_batch(data, 'hired_employees', conn)
 
        cursor = conn.cursor()
        for record in validation_result['valid']:
            try:
                cursor.execute(
                    '''INSERT INTO hired_employees
                       (id, name, datetime, department_id, job_id)
                       VALUES (?, ?, ?, ?, ?)''',
                    (record['id'], record['name'], record['datetime'],
                     record['department_id'], record['job_id'])
                )
            except Exception as e:
                logger.error(f"hired_employees | ID: {record.get('id')} | Database error: {str(e)}")
 
        conn.commit()
        conn.close()
 
        response = {
            'status': 'success' if validation_result['stats']['invalid'] == 0 else 'partial',
            'total_rows': validation_result['stats']['total'],
            'inserted': validation_result['stats']['valid'],
            'rejected': validation_result['stats']['invalid'],
            'errors': None
        }
 
        if validation_result['invalid']:
            response['errors'] = [
                {'row_index': err['row_index'], 'errors': err['errors']}
                for err in validation_result['invalid']
            ]
 
        return jsonify(response), 200
 
    except Exception as e:
        logger.error(f"hired_employees endpoint error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
 
 
# ============================================================================
# BACKUP & RESTORE ENDPOINTS
# ============================================================================
 
@app.route('/api/backup', methods=['GET'])
def backup():
    """Backup a table to AVRO format"""
    try:
        table_name = request.args.get('table', None)
 
        if not table_name:
            return jsonify({
                'status': 'error',
                'message': 'Please specify a table name. Example: /api/backup?table=departments'
            }), 400
 
        valid_tables = ['departments', 'jobs', 'hired_employees']
        if table_name not in valid_tables:
            return jsonify({
                'status': 'error',
                'message': f'Invalid table name. Valid options: {", ".join(valid_tables)}'
            }), 400
 
        result = backup_table(table_name)
 
        if result:
            return jsonify({
                'status': 'success',
                'table': table_name,
                'filename': result['filename'],
                'rows_backed_up': result['rows'],
                'timestamp': result['timestamp']
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'No data found in table {table_name}'
            }), 404
 
    except Exception as e:
        logger.error(f"Backup error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
 
 
@app.route('/api/restore', methods=['POST'])
def restore():
    """Restore a table from AVRO backup"""
    try:
        data = request.json
        if not data or 'filename' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Please provide a filename. Example: {"filename": "backup/departments_20240115.avro"}'
            }), 400
 
        filename = data['filename']
        success, message = restore_table(filename)
 
        if success:
            return jsonify({
                'status': 'success',
                'message': message
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': message
            }), 400
 
    except Exception as e:
        logger.error(f"Restore error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
 
 
@app.route('/api/backups', methods=['GET'])
def get_backups():
    """List all available backups"""
    try:
        backups = list_backups()
        return jsonify({
            'status': 'success',
            'backups': backups
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
 
 
# ============================================================================
# ANALYSIS ENDPOINTS (Challenge #2)
# ============================================================================
 
@app.route('/api/analysis/employees-by-quarter', methods=['GET'])
def analysis_employees_by_quarter():
    """Get employees hired per job and department by quarter (2021 only)"""
    conn = get_connection()
    cursor = conn.cursor()
 
    query = '''
    SELECT
        d.department,
        j.job,
        COUNT(CASE WHEN CAST(strftime('%m', he.datetime) AS INTEGER) BETWEEN 1 AND 3 THEN 1 END) as Q1,
        COUNT(CASE WHEN CAST(strftime('%m', he.datetime) AS INTEGER) BETWEEN 4 AND 6 THEN 1 END) as Q2,
        COUNT(CASE WHEN CAST(strftime('%m', he.datetime) AS INTEGER) BETWEEN 7 AND 9 THEN 1 END) as Q3,
        COUNT(CASE WHEN CAST(strftime('%m', he.datetime) AS INTEGER) BETWEEN 10 AND 12 THEN 1 END) as Q4
    FROM hired_employees he
    JOIN departments d ON he.department_id = d.id
    JOIN jobs j ON he.job_id = j.id
    WHERE CAST(strftime('%Y', he.datetime) AS INTEGER) = 2021
    GROUP BY d.department, j.job
    ORDER BY d.department, j.job
    '''
 
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
 
    result = []
    for row in rows:
        result.append({
            'department': row[0],
            'job': row[1],
            'Q1': row[2],
            'Q2': row[3],
            'Q3': row[4],
            'Q4': row[5]
        })
 
    return jsonify({
        'status': 'success',
        'data': result
    }), 200
 
 
@app.route('/api/analysis/departments-above-average', methods=['GET'])
def analysis_departments_above_average():
    """Get departments with above average hiring (2021 only)"""
    conn = get_connection()
    cursor = conn.cursor()
 
    query = '''
    WITH dept_hiring AS (
        SELECT
            d.id,
            d.department,
            COUNT(*) as hired
        FROM hired_employees he
        JOIN departments d ON he.department_id = d.id
        WHERE CAST(strftime('%Y', he.datetime) AS INTEGER) = 2021
        GROUP BY d.id, d.department
    ),
    avg_hired AS (
        SELECT AVG(hired) as avg_hired FROM dept_hiring
    )
    SELECT d.id, d.department, d.hired
    FROM dept_hiring d, avg_hired a
    WHERE d.hired > a.avg_hired
    ORDER BY d.hired DESC
    '''
 
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
 
    result = []
    for row in rows:
        result.append({
            'id': row[0],
            'department': row[1],
            'hired': row[2]
        })
 
    return jsonify({
        'status': 'success',
        'data': result
    }), 200
 
 
# ============================================================================
# ERROR HANDLERS
# ============================================================================
 
@app.errorhandler(400)
def bad_request(e):
    return jsonify({'status': 'error', 'message': 'Bad request'}), 400
 
@app.errorhandler(404)
def not_found(e):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404
 
@app.errorhandler(500)
def server_error(e):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
 
 
if __name__ == '__main__':
    app.run(debug=True, port=5000)