import sqlite3

conn = sqlite3.connect('nutrition_app.db')
cursor = conn.cursor()

# Get all logs with image paths
cursor.execute('SELECT log_id, image_path FROM food_logs WHERE image_path IS NOT NULL')
logs = cursor.fetchall()

print(f'Found {len(logs)} meals with images')
print('Fixing paths...\n')

for log_id, image_path in logs:
    # Remove 'uploads\' or 'uploads/' from the path
    if image_path and ('uploads\\' in image_path or 'uploads/' in image_path):
        new_path = image_path.replace('uploads\\', '').replace('uploads/', '')
        cursor.execute('UPDATE food_logs SET image_path = ? WHERE log_id = ?', (new_path, log_id))
        print(f'✓ Fixed log {log_id}: {image_path} -> {new_path}')
    else:
        print(f'  Log {log_id}: {image_path} (already correct)')

conn.commit()
conn.close()
print('\n✅ All image paths fixed!')