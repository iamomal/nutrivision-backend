import sqlite3
from datetime import datetime

def create_database():
    """Create the nutritional analysis database with all required tables"""
    conn = sqlite3.connect('nutrition_app.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
    ''')
    
    # User goals table - CORRECTED SCHEMA
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_goals (
        goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        weekly_points_target INTEGER DEFAULT 100,
        calorie_target INTEGER,
        protein_target REAL,
        carbs_target REAL,
        fat_target REAL,
        goal_type VARCHAR(50),
        start_date DATE NOT NULL,
        end_date DATE,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    ''')
    
    # Food logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS food_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        food_name VARCHAR(100) NOT NULL,
        confidence_score REAL,
        image_path VARCHAR(255),
        meal_type VARCHAR(20),
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        calories REAL,
        protein REAL,
        carbs REAL,
        fat REAL,
        points_awarded INTEGER,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    ''')
    
    # Weekly progress table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weekly_progress (
        progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        week_start_date DATE NOT NULL,
        week_end_date DATE NOT NULL,
        total_points INTEGER DEFAULT 0,
        meals_logged INTEGER DEFAULT 0,
        total_calories REAL DEFAULT 0,
        total_protein REAL DEFAULT 0,
        total_carbs REAL DEFAULT 0,
        total_fat REAL DEFAULT 0,
        goal_achieved BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        UNIQUE(user_id, week_start_date)
    )
    ''')
    
    # Nutritional database (reference for food items)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS food_nutrition (
        food_id INTEGER PRIMARY KEY AUTOINCREMENT,
        food_name VARCHAR(100) UNIQUE NOT NULL,
        calories REAL NOT NULL,
        protein REAL NOT NULL,
        carbs REAL NOT NULL,
        fat REAL NOT NULL,
        serving_size VARCHAR(50),
        health_score INTEGER DEFAULT 50,
        category VARCHAR(50)
    )
    ''')
    
    # Achievements/Badges table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS achievements (
        achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        achievement_type VARCHAR(50) NOT NULL,
        achievement_name VARCHAR(100) NOT NULL,
        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_achievements (
        achievement_id TEXT PRIMARY KEY,
        user_id INTEGER,
        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        points_awarded INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database created successfully!")

def insert_sample_nutrition_data():
    """Insert sample nutritional data for Food-101 categories"""
    conn = sqlite3.connect('nutrition_app.db')
    cursor = conn.cursor()
    
    # Sample nutritional data (per serving)
    sample_foods = [
        ('apple_pie', 237, 2, 34, 11, '1 slice', 45, 'dessert'),
        ('caesar_salad', 184, 6, 8, 15, '1 bowl', 65, 'salad'),
        ('chicken_curry', 350, 25, 20, 18, '1 cup', 70, 'main'),
        ('chocolate_cake', 352, 5, 50, 14, '1 slice', 30, 'dessert'),
        ('french_fries', 312, 4, 41, 15, '1 serving', 35, 'side'),
        ('grilled_salmon', 280, 39, 0, 13, '6 oz', 95, 'main'),
        ('greek_salad', 150, 4, 8, 12, '1 bowl', 85, 'salad'),
        ('hamburger', 354, 20, 30, 17, '1 burger', 50, 'main'),
        ('pizza', 285, 12, 36, 10, '2 slices', 40, 'main'),
        ('sushi', 200, 9, 28, 5, '6 pieces', 75, 'main'),
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO food_nutrition 
    (food_name, calories, protein, carbs, fat, serving_size, health_score, category)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_foods)
    
    conn.commit()
    conn.close()
    print("Sample nutrition data inserted!")

if __name__ == "__main__":
    create_database()
    insert_sample_nutrition_data()