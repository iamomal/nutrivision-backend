import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3

def init_database():
    # Always get DATABASE_URL from environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        print("⚠️ No DATABASE_URL found in environment, using SQLite for development")
        create_sqlite_database()
        return
    
    try:
        print(f"Attempting to connect to PostgreSQL...")
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("✅ Connected to PostgreSQL successfully!")
        
        # Create the tables for your nutrition app (only if they don't exist)
        create_nutrition_tables(cursor)
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("⚠️ Falling back to SQLite for development...")
        create_sqlite_database()

def create_nutrition_tables(cursor):
    """Create tables for the nutrition application (only if they don't exist)"""
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            profile_picture VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Create food_nutrition table (for storing nutrition data of foods)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_nutrition (
            food_id SERIAL PRIMARY KEY,
            food_name VARCHAR(100) UNIQUE NOT NULL,
            calories INTEGER NOT NULL,
            protein DECIMAL(8,2) NOT NULL,
            carbs DECIMAL(8,2) NOT NULL,
            fat DECIMAL(8,2) NOT NULL,
            health_score INTEGER NOT NULL
        )
    ''')
    
    # Create user_goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_goals (
            goal_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
            goal_type VARCHAR(50) NOT NULL DEFAULT 'maintain',
            weekly_points_target INTEGER DEFAULT 100,
            calorie_target INTEGER DEFAULT 2000,
            protein_target INTEGER DEFAULT 120,
            goal_description TEXT,
            start_date DATE NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create food_logs table (for logging user food entries)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_logs (
            log_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
            food_name VARCHAR(100) NOT NULL,
            confidence_score DECIMAL(5,4) NOT NULL,
            image_path VARCHAR(255) NOT NULL,
            meal_type VARCHAR(20) NOT NULL,
            calories INTEGER NOT NULL,
            protein DECIMAL(8,2) NOT NULL,
            carbs DECIMAL(8,2) NOT NULL,
            fat DECIMAL(8,2) NOT NULL,
            points_awarded INTEGER NOT NULL,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create weekly_progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_progress (
            progress_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
            week_start_date DATE NOT NULL,
            week_end_date DATE NOT NULL,
            total_points INTEGER DEFAULT 0,
            meals_logged INTEGER DEFAULT 0,
            total_calories INTEGER DEFAULT 0,
            total_protein DECIMAL(10,2) DEFAULT 0,
            total_carbs DECIMAL(10,2) DEFAULT 0,
            total_fat DECIMAL(10,2) DEFAULT 0,
            UNIQUE(user_id, week_start_date)
        )
    ''')
    
    # Create user_achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_achievements (
            achievement_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
            achievement_key VARCHAR(50) NOT NULL,
            achievement_name VARCHAR(100) NOT NULL,
            achievement_description TEXT,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            points_awarded INTEGER DEFAULT 0
        )
    ''')
    
    print("✅ Nutrition app tables created/verified successfully!")

def create_sqlite_database():
    """Create SQLite database as fallback"""
    conn = sqlite3.connect('nutrition_app.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            profile_picture VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    ''')
    
    # Create food_nutrition table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_nutrition (
            food_id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_name VARCHAR(100) UNIQUE NOT NULL,
            calories INTEGER NOT NULL,
            protein DECIMAL(8,2) NOT NULL,
            carbs DECIMAL(8,2) NOT NULL,
            fat DECIMAL(8,2) NOT NULL,
            health_score INTEGER NOT NULL
        )
    ''')
    
    # Create user_goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_goals (
            goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            goal_type VARCHAR(50) NOT NULL DEFAULT 'maintain',
            weekly_points_target INTEGER DEFAULT 100,
            calorie_target INTEGER DEFAULT 2000,
            protein_target INTEGER DEFAULT 120,
            goal_description TEXT,
            start_date DATE NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Create food_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            food_name VARCHAR(100) NOT NULL,
            confidence_score DECIMAL(5,4) NOT NULL,
            image_path VARCHAR(255) NOT NULL,
            meal_type VARCHAR(20) NOT NULL,
            calories INTEGER NOT NULL,
            protein DECIMAL(8,2) NOT NULL,
            carbs DECIMAL(8,2) NOT NULL,
            fat DECIMAL(8,2) NOT NULL,
            points_awarded INTEGER NOT NULL,
            logged_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Create weekly_progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_progress (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            week_start_date DATE NOT NULL,
            week_end_date DATE NOT NULL,
            total_points INTEGER DEFAULT 0,
            meals_logged INTEGER DEFAULT 0,
            total_calories INTEGER DEFAULT 0,
            total_protein DECIMAL(10,2) DEFAULT 0,
            total_carbs DECIMAL(10,2) DEFAULT 0,
            total_fat DECIMAL(10,2) DEFAULT 0,
            UNIQUE(user_id, week_start_date),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Create user_achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_achievements (
            achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_key VARCHAR(50) NOT NULL,
            achievement_name VARCHAR(100) NOT NULL,
            achievement_description TEXT,
            earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            points_awarded INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ SQLite database created successfully!")

if __name__ == '__main__':
    init_database()