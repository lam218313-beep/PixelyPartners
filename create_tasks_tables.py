"""
Script to create tasks and task_notes tables in the database.
Run this once to add task management tables.

Usage:
    python create_tasks_tables.py
"""

import sys
from api.database import engine, Base
from api.models_tasks import Task, TaskNote

def create_tables():
    """Create tasks and task_notes tables."""
    print("🔧 Creating tasks tables...")
    
    try:
        # Import all models to ensure they're registered with Base
        from api import models  # Import main models
        
        # Create only the new tables
        Task.__table__.create(engine, checkfirst=True)
        TaskNote.__table__.create(engine, checkfirst=True)
        
        print("✅ Tasks tables created successfully!")
        print("   - tasks")
        print("   - task_notes")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_tables()
