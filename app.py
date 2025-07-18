"""
Super simple FastAPI application for Railway deployment with database connection test
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import psycopg2
from typing import Dict, Any, List

app = FastAPI()

# Get database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def read_root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "Hello from Railway!",
        "database_url_exists": bool(DATABASE_URL),
        "environment": os.environ.get("ENVIRONMENT", "development")
    }

@app.get("/health")
def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/db-test")
def test_db_connection() -> Dict[str, Any]:
    """Test database connection"""
    if not DATABASE_URL:
        return {"status": "error", "message": "No DATABASE_URL environment variable found"}
    
    try:
        # Connect to the database
        conn = psycopg2.connect(DATABASE_URL)
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Execute a simple query
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        
        # Fetch all results
        tables = [row[0] for row in cursor.fetchall()]
        
        # Close the connection
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Successfully connected to the database",
            "tables": tables
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to connect to the database: {str(e)}"
        }

@app.get("/env")
def show_environment() -> Dict[str, Any]:
    """Show environment variables (excluding sensitive ones)"""
    env_vars = {}
    for key, value in os.environ.items():
        # Skip sensitive variables
        if any(sensitive in key.lower() for sensitive in ["password", "secret", "key", "token"]):
            env_vars[key] = "***REDACTED***"
        else:
            env_vars[key] = value
    return {"environment_variables": env_vars}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}")
    print(f"Database URL exists: {bool(DATABASE_URL)}")
    uvicorn.run(app, host="0.0.0.0", port=port)