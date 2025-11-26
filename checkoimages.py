import sqlite3

conn = sqlite3.connect('nutrition_app.db')
cursor = conn.cursor()
cursor.execute('SELECT log_id, food_name, image_path FROM food_logs ORDER BY log_id DESC LIMIT 5')
print('Recent meal logs:')
for row in cursor.fetchall():
    print(f'ID: {row[0]}, Food: {row[1]}, Image: {row[2]}')
conn.close()