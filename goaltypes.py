import sqlite3

conn = sqlite3.connect('nutrition_app.db')
cursor = conn.cursor()

# Add goal_type column if it doesn't exist
try:
    cursor.execute('ALTER TABLE user_goals ADD COLUMN goal_type VARCHAR(50) DEFAULT "maintain"')
    print('Added goal_type column')
except sqlite3.OperationalError:
    print('goal_type column already exists')

# Add goal_description column
try:
    cursor.execute('ALTER TABLE user_goals ADD COLUMN goal_description TEXT')
    print('Added goal_description column')
except sqlite3.OperationalError:
    print('goal_description column already exists')

conn.commit()
conn.close()
print('✅ Database updated!')