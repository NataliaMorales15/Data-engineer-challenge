"""
REST API Module - Flask Application
Handles all API endpoints for data ingestion and analysis
"""

from flask import Flask, request, jsonify
from database import get_connection, get_table_count
from validation import validate_batch, validate_hired_employee, validate_department, validate_job
import logging
import json

# Initialize Flask app
app = Flask(__name__)

# Setup logging
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
    """
    Ingest departments
    
    POST /api/departments
    {
        "data": [
            {"id": 1, "department": "Engineering"},
            {"id": 2, "department": "Sales"}
        ]
    }
    """
    try:
        data = request.json.get('data', [])
        
        # Validate batch size
        if not isinstance(data, list):
            return jsonify({
                'status': 'error',
                'message': 'Data must be a list'
            }), 400
        
        if len(data) > 1000:
            return jsonify({
                'status': 'error',
                'message': 'Batch size cannot exceed 1000 records'
            }), 400
        
        if len(data) == 0:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # Validate records
        conn = get_connection()
        validation_result = validate_batch(data, 'departments', conn)
        
        # Insert valid records
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
        
        # Build response
        response = {
            'status': 'success' if validation_result['stats']['invalid'] == 0 else 'partial',
            'total_rows': validation_result['stats']['total'],
            'inserted': validation_result['stats']['valid'],
            'rejected': validation_result['stats']['invalid'],
            'errors': None
        }
        
        if validation_result['invalid']:
            response['errors'] = [
                {
                    'row_index': err['row_index'],
                    'errors': err['errors']
                }
                for err in validation_result['invalid']
            ]
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"departments endpoint error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/jobs', methods=['POST'])
def ingest_jobs():
    """
    Ingest jobs
    
    POST /api/jobs
    {
        "data": [
            {"id": 1, "job": "Software Engineer"},
            {"id": 2, "job": "Data Scientist"}
        ]
    }
    """
    try:
        data = request.json.get('data', [])
        
        # Validate batch size
        if not isinstance(data, list):
            return jsonify({
                'status': 'error',
                'message': 'Data must be a list'
            }), 400
        
        if len(data) > 1000:
            return jsonify({
                'status': 'error',
                'message': 'Batch size cannot exceed 1000 records'
            }), 400
        
        if len(data) == 0:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # Validate records
        conn = get_connection()
        validation_result = validate_batch(data, 'jobs', conn)
        
        # Insert valid records
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
        
        # Build response
        response = {
            'status': 'success' if validation_result['stats']['invalid'] == 0 else 'partial',
            'total_rows': validation_result['stats']['total'],
            'inserted': validation_result['stats']['valid'],
            'rejected': validation_result['stats']['invalid'],
            'errors': None
        }
        
        if validation_result['invalid']:
            response['errors'] = [
                {
                    'row_index': err['row_index'],
                    'errors': err['errors']
                }
                for err in validation_result['invalid']
            ]
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"jobs endpoint error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/hired_employees', methods=['POST'])
def ingest_hired_employees():
    """
    Ingest hired employees
    
    POST /api/hired_employees
    {
        "data": [
            {
                "id": 1,
                "name": "John Doe",
                "datetime": "2021-03-15T10:30:00Z",
                "department_id": 1,
                "job_id": 1
            }
        ]
    }
    """
    try:
        data = request.json.get('data', [])
        
        # Validate batch size
        if not isinstance(data, list):
            return jsonify({
                'status': 'error',
                'message': 'Data must be a list'
            }), 400
        
        if len(data) > 1000:
            return jsonify({
                'status': 'error',
                'message': 'Batch size cannot exceed 1000 records'
            }), 400
        
        if len(data) == 0:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # Validate records
        conn = get_connection()
        validation_result = validate_batch(data, 'hired_employees', conn)
        
        # Insert valid records
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
        
        # Build response
        response = {
            'status': 'success' if validation_result['stats']['invalid'] == 0 else 'partial',
            'total_rows': validation_result['stats']['total'],
            'inserted': validation_result['stats']['valid'],
            'rejected': validation_result['stats']['invalid'],
            'errors': None
        }
        
        if validation_result['invalid']:
            response['errors'] = [
                {
                    'row_index': err['row_index'],
                    'errors': err['errors']
                }
                for err in validation_result['invalid']
            ]
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"hired_employees endpoint error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(400)
def bad_request(e):
    """Handle 400 Bad Request"""
    return jsonify({
        'status': 'error',
        'message': 'Bad request'
    }), 400

@app.errorhandler(404)
def not_found(e):
    """Handle 404 Not Found"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 Server Error"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

# ============================================================================
# APP CONFIGURATION
# ============================================================================

@app.before_request
def log_request():
    """Log incoming requests"""
    if request.method in ['POST', 'GET']:
        pass  # Uncomment for debugging: print(f"{request.method} {request.path}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
