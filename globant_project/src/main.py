"""
Globant Data Engineer Challenge - Main Entry Point
"""
 
import sys
import os
 
# Get the directory where this script is located (src/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
 
# Get the project root (one level up from src/)
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
 
# Add src folder to Python path so imports work
sys.path.insert(0, SCRIPT_DIR)
 
# Change working directory to project root so data/, backup/, logs/ are found
os.chdir(PROJECT_DIR)
 
from database import init_database, load_historical_data, check_data_quality
from api import app
 
 
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
        print("✅ Data loaded successfully!")
        print(f"   - Departments: {stats['departments']} records")
        print(f"   - Jobs: {stats['jobs']} records")
        print(f"   - Hired Employees: {stats['hired_employees']} records")
 
        # Check data quality
        print("\n🔍 Checking data quality...")
        quality_report = check_data_quality()
        print("✅ Data quality check complete:")
        print(f"   - Valid employees: {quality_report.get('valid_employees', 0)}")
        print(f"   - Invalid employees: {quality_report.get('invalid_employees', 0)}")
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
        print("   - GET    /api/stats")
        print("=" * 60)
 
        app.run(debug=True, port=5000, use_reloader=False)
 
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
 
 
if __name__ == '__main__':
    main()