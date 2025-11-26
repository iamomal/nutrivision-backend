import sqlite3

conn = sqlite3.connect('nutrition_app.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT food_name, calories, protein, health_score, category 
    FROM food_nutrition 
    WHERE food_name IN ("creme_brulee", "pizza", "baklava")
''')

print('Food Health Scores and Details:')
print('-' * 60)
for row in cursor.fetchall():
    print(f'{row[0]:20} | Calories: {row[1]:4} | Protein: {row[2]:2}g | Health: {row[3]:2} | Category: {row[4]}')

conn.close()