"""
Globant Data Engineer Challenge - Main Entry Point
Handles database initialization, data loading, and API startup
"""

from database import init_database, load_historical_data, check_data_quality
from api import app
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    print("=" * 60)
    print("🚀 GLOBANT DATA ENGINEER CHALLENGE - DATA INGESTION")
    print("=" * 60)
    
    try:
        # Create necessary directories
        print("\n📁 Creating project directories...")
        os.makedirs('data', exist_ok=True)
        os.makedirs('backup', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        print("✅ Directories created")
        
        # Initialize database
        print("\n🗄️  Initializing database...")
        init_database()
        print("✅ Database initialized")
        
        # Load historical data
        print("\n📥 Loading historical data from CSV files...")
        stats = load_historical_data()
        print(f"✅ Data loaded successfully!")
        print(f"   - Departments: {stats['departments']} records")
        print(f"   - Jobs: {stats['jobs']} records")
        print(f"   - Hired Employees: {stats['hired_employees']} records")
        
        # Check data quality
        print("\n🔍 Checking data quality...")
        quality_report = check_data_quality()
        print(f"✅ Data quality check complete:")
        print(f"   - Valid employees: {quality_report['valid_employees']}")
        print(f"   - Invalid employees: {quality_report['invalid_employees']}")
        print(f"   - Issues found and logged to: logs/error.log")
        
        # Start API
        print("\n" + "=" * 60)
        print("🌐 STARTING REST API SERVER")
        print("=" * 60)
        print("\n✅ API running at: http://localhost:5000")
        print("\n📋 Available Endpoints:")
        print("   Ingestion:")
        print("   - POST   /api/departments")
        print("   - POST   /api/jobs")
        print("   - POST   /api/hired_employees")
        print("\n   Analysis:")
        print("   - GET    /api/analysis/employees-by-quarter")
        print("   - GET    /api/analysis/departments-above-average")
        print("\n   Backup/Restore:")
        print("   - GET    /api/backup?table=<table_name>")
        print("   - POST   /api/restore")
        print("\n   Utility:")
        print("   - GET    /health")
        print("\n💡 Test with: curl http://localhost:5000/health")
        print("=" * 60)
        
        # Start Flask app
        app.run(debug=True, port=5000, use_reloader=False)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Error: {e}")
        exit(1)

if __name__ == '__main__':
    main()
