#!/usr/bin/env python3
"""
Database initialization script for SMS application.
This script creates all necessary tables and initial data.
"""

import asyncio
import os
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.core.database import engine
from app.core.config import settings
from sqlalchemy import text


async def create_tables():
    """Create all database tables and initial data."""
    
    # SQL commands to create tables and initial data
    sql_commands = [
        # Create roles table
        """
        CREATE TABLE IF NOT EXISTS roles (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL,
            description VARCHAR(255)
        );
        """,
        
        # Create users table
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Create user_roles association table
        """
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
            PRIMARY KEY (user_id, role_id)
        );
        """,
        
        # Create classes table
        """
        CREATE TABLE IF NOT EXISTS classes (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            section VARCHAR(50),
            academic_year VARCHAR(20) NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            teacher_id INTEGER
        );
        """,
        
        # Create subjects table
        """
        CREATE TABLE IF NOT EXISTS subjects (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(20) UNIQUE NOT NULL,
            description TEXT,
            credits INTEGER,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Create students table
        """
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            admission_number VARCHAR(50) UNIQUE NOT NULL,
            roll_number VARCHAR(50),
            date_of_birth DATE,
            gender VARCHAR(20) DEFAULT 'not_specified',
            blood_group VARCHAR(10) DEFAULT 'Not Known',
            class_id INTEGER REFERENCES classes(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Create grades table
        """
        CREATE TABLE IF NOT EXISTS grades (
            id SERIAL PRIMARY KEY,
            value DECIMAL(5,2) NOT NULL,
            max_value DECIMAL(5,2) DEFAULT 100.0,
            grade_type VARCHAR(20) DEFAULT 'other',
            term VARCHAR(50),
            description TEXT,
            graded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE
        );
        """,
        
        # Create examinations table
        """
        CREATE TABLE IF NOT EXISTS examinations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            exam_type VARCHAR(20) DEFAULT 'other',
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            description TEXT,
            is_published BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Insert default roles
        """
        INSERT INTO roles (name, description) VALUES 
            ('admin', 'System Administrator'),
            ('teacher', 'Teacher/Staff Member'),
            ('student', 'Student'),
            ('parent', 'Parent/Guardian')
        ON CONFLICT (name) DO NOTHING;
        """,
        
        # Insert default admin user (password: admin123)
        """
        INSERT INTO users (username, email, first_name, last_name, hashed_password, is_active, is_verified) VALUES 
            ('admin', 'admin@sms.local', 'System', 'Administrator', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5/Qe2', TRUE, TRUE)
        ON CONFLICT (username) DO NOTHING;
        """,
        
        # Assign admin role to admin user
        """
        INSERT INTO user_roles (user_id, role_id) 
        SELECT u.id, r.id FROM users u, roles r 
        WHERE u.username = 'admin' AND r.name = 'admin'
        ON CONFLICT DO NOTHING;
        """,
        
        # Create indexes for better performance
        """
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_students_admission_number ON students(admission_number);
        CREATE INDEX IF NOT EXISTS idx_subjects_code ON subjects(code);
        CREATE INDEX IF NOT EXISTS idx_grades_student_id ON grades(student_id);
        CREATE INDEX IF NOT EXISTS idx_grades_subject_id ON grades(subject_id);
        """
    ]
    
    try:
        async with engine.begin() as conn:
            logger.info("🗄️ Creating database tables...")
            
            for i, sql_command in enumerate(sql_commands, 1):
                try:
                    await conn.execute(text(sql_command))
                    logger.info(f"✅ Executed command {i}/{len(sql_commands)}")
                except Exception as e:
                    logger.warning(f"⚠️ Warning in command {i}: {e}")
                    continue
            
            logger.info("✅ Database initialization completed successfully!")
            
            # Verify tables were created
            result = await conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"📋 Created tables: {', '.join(tables)}")
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def main():
    """Main function to initialize database."""
    logger.info("🚀 Starting SMS Database Initialization...")
    logger.info(f"📍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔗 Database URL: {str(settings.SQLALCHEMY_DATABASE_URI)[:50]}...")
    
    await create_tables()
    await engine.dispose()
    
    logger.info("🎉 Database setup completed!")


if __name__ == "__main__":
    asyncio.run(main())