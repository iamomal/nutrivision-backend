import sqlite3

conn = sqlite3.connect('nutrition_app.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT user_id, goal_type, weekly_points_target, is_active 
    FROM user_goals 
    ORDER BY goal_id DESC
''')

print('User Goals:')
print('-' * 60)
results = cursor.fetchall()
if results:
    for row in results:
        status = "ACTIVE" if row[3] else "inactive"
        print(f'User {row[0]} | Goal: {row[1] or "None"} | Target: {row[2]} | Status: {status}')
else:
    print('No goals found')

conn.close()