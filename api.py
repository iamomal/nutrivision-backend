from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import jwt
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load model
model = tf.keras.models.load_model('nutritional_analysis_model.h5')

CLASS_NAMES = ['apple_pie', 'baby_back_ribs', 'baklava', 'beef_carpaccio', 'beef_tartare', 
               'beet_salad', 'beignets', 'bibimbap', 'bread_pudding', 'breakfast_burrito',
               'bruschetta', 'caesar_salad', 'cannoli', 'caprese_salad', 'carrot_cake',
               'ceviche', 'cheesecake', 'cheese_plate', 'chicken_curry', 'chicken_quesadilla',
               'chicken_wings', 'chocolate_cake', 'chocolate_mousse', 'churros', 'clam_chowder',
               'club_sandwich', 'crab_cakes', 'creme_brulee', 'croque_madame', 'cup_cakes',
               'deviled_eggs', 'donuts', 'dumplings', 'edamame', 'eggs_benedict',
               'escargots', 'falafel', 'filet_mignon', 'fish_and_chips', 'foie_gras',
               'french_fries', 'french_onion_soup', 'french_toast', 'fried_calamari', 'fried_rice',
               'frozen_yogurt', 'garlic_bread', 'gnocchi', 'greek_salad', 'grilled_cheese_sandwich',
               'grilled_salmon', 'guacamole', 'gyoza', 'hamburger', 'hot_and_sour_soup',
               'hot_dog', 'huevos_rancheros', 'hummus', 'ice_cream', 'lasagna',
               'lobster_bisque', 'lobster_roll_sandwich', 'macaroni_and_cheese', 'macarons', 'miso_soup',
               'mussels', 'nachos', 'omelette', 'onion_rings', 'oysters',
               'pad_thai', 'paella', 'pancakes', 'panna_cotta', 'peking_duck',
               'pho', 'pizza', 'pork_chop', 'poutine', 'prime_rib',
               'pulled_pork_sandwich', 'ramen', 'ravioli', 'red_velvet_cake', 'risotto',
               'samosa', 'sashimi', 'scallops', 'seaweed_salad', 'shrimp_and_grits',
               'spaghetti_bolognese', 'spaghetti_carbonara', 'spring_rolls', 'steak', 'strawberry_shortcake',
               'sushi', 'tacos', 'takoyaki', 'tiramisu', 'tuna_tartare', 'waffles']

# Database helper
def get_db():
    conn = sqlite3.connect('nutrition_app.db')
    conn.row_factory = sqlite3.Row
    return conn

# JWT token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated

# Authentication endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
    if cursor.fetchone():
        conn.close()
        return jsonify({'message': 'User already exists'}), 409
    
    # Create user
    password_hash = generate_password_hash(password)
    cursor.execute('''
        INSERT INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
    ''', (username, email, password_hash))
    
    user_id = cursor.lastrowid
    
    # Create default goal
    cursor.execute('''
        INSERT INTO user_goals (user_id, weekly_points_target, start_date)
        VALUES (?, 100, ?)
    ''', (user_id, datetime.now().date()))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user or not check_password_hash(user['password_hash'], password):
        conn.close()
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Update last login
    cursor.execute('UPDATE users SET last_login = ? WHERE user_id = ?', 
                   (datetime.now(), user['user_id']))
    conn.commit()
    conn.close()
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user['user_id'],
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        'token': token,
        'user_id': user['user_id'],
        'username': user['username']
    }), 200

# Food prediction endpoint
# Food prediction endpoint
@app.route('/api/predict', methods=['POST'])
@token_required
def predict_food(current_user_id):
    if 'image' not in request.files:
        return jsonify({'message': 'No image provided'}), 400
    
    file = request.files['image']
    meal_type = request.form.get('meal_type', 'other')
    
    # Preprocess image
    img = Image.open(io.BytesIO(file.read())).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predict
    predictions = model.predict(img_array)
    top_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][top_idx])
    food_name = CLASS_NAMES[top_idx]
    
    # Get nutrition info
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM food_nutrition WHERE food_name = ?', (food_name,))
    nutrition = cursor.fetchone()
    
    if nutrition:
        nutrition_data = dict(nutrition)
    else:
        # Default values if not in database
        nutrition_data = {
            'calories': 250,
            'protein': 10,
            'carbs': 30,
            'fat': 10,
            'health_score': 50
        }
    
    # Fetch user's goal to adjust points
    cursor.execute('''
        SELECT goal_type FROM user_goals 
        WHERE user_id = ? AND is_active = 1
        ORDER BY goal_id DESC LIMIT 1
    ''', (current_user_id,))
    goal_row = cursor.fetchone()
    goal_type = goal_row['goal_type'] if goal_row else 'maintain'
    
    # Calculate points with goal consideration
    points = calculate_points(nutrition_data, goal_type)
    
    # Save image
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{current_user_id}_{timestamp}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img.save(filepath)
    
    # Log food
    cursor.execute('''
        INSERT INTO food_logs 
        (user_id, food_name, confidence_score, image_path, meal_type, 
         calories, protein, carbs, fat, points_awarded)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (current_user_id, food_name, confidence, filename, meal_type,
          nutrition_data['calories'], nutrition_data['protein'], 
          nutrition_data['carbs'], nutrition_data['fat'], points))
    
    conn.commit()
    
    # Update weekly progress
    update_weekly_progress(current_user_id, points, nutrition_data)
    
    conn.close()
    
    return jsonify({
        'food_name': food_name.replace('_', ' ').title(),
        'confidence': confidence,
        'nutrition': nutrition_data,
        'points_awarded': points,
        'goal_type': goal_type  # Optional: return goal type so frontend can show context
    }), 200

def calculate_points(nutrition, goal_type='maintain'):
    """Calculate points based on nutritional value and user goal"""
    health_score = nutrition.get('health_score', 50)
    calories = nutrition.get('calories', 0)
    protein = nutrition.get('protein', 0)
    
    # Base points from health score
    if health_score >= 80:
        base_points = 15
    elif health_score >= 60:
        base_points = 10
    elif health_score >= 40:
        base_points = 5
    else:
        base_points = -5
    
    # Apply goal-specific modifiers
    if goal_type == 'lose_weight':
        # Penalize high-calorie foods more, reward low-calorie nutrient-dense foods
        if calories > 400:
            base_points -= 5
        elif calories < 250 and health_score >= 70:
            base_points += 10
        
        # Extra penalty for unhealthy high-calorie foods
        if calories > 300 and health_score < 40:
            base_points -= 5
            
    elif goal_type == 'gain_weight':
        # Reward high-protein foods significantly
        if protein > 25:
            base_points += 10
        elif protein > 15:
            base_points += 5
        
        # Reward calorie-dense healthy foods
        if calories > 350 and health_score >= 60:
            base_points += 5
        
        # Don't penalize junk food as much (still need calories)
        if health_score < 40:
            base_points = max(base_points, 0)  # No negative points
            
    elif goal_type == 'eat_healthier':
        # Maximum emphasis on health score
        if health_score >= 85:
            base_points += 15
        elif health_score >= 70:
            base_points += 10
        elif health_score < 40:
            base_points -= 10
        
        # Severely penalize junk food
        if health_score < 30:
            base_points -= 5
            
    elif goal_type == 'athletic':
        # Reward protein
        if protein > 25:
            base_points += 10
        elif protein > 15:
            base_points += 5
        
        # Reward healthy foods
        if health_score >= 70:
            base_points += 5
    
    # Ensure minimum and maximum bounds
    return max(min(base_points, 25), -15)  # Between -15 and +25 points

def update_weekly_progress(user_id, points, nutrition):
    """Update weekly progress for the user"""
    conn = get_db()
    cursor = conn.cursor()
    
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    cursor.execute('''
        INSERT INTO weekly_progress 
        (user_id, week_start_date, week_end_date, total_points, meals_logged,
         total_calories, total_protein, total_carbs, total_fat)
        VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?)
        ON CONFLICT(user_id, week_start_date) DO UPDATE SET
            total_points = total_points + ?,
            meals_logged = meals_logged + 1,
            total_calories = total_calories + ?,
            total_protein = total_protein + ?,
            total_carbs = total_carbs + ?,
            total_fat = total_fat + ?
    ''', (user_id, week_start, week_end, points,
          nutrition['calories'], nutrition['protein'], nutrition['carbs'], nutrition['fat'],
          points, nutrition['calories'], nutrition['protein'], nutrition['carbs'], nutrition['fat']))
    
    conn.commit()
    conn.close()

# Get user progress
@app.route('/api/progress', methods=['GET'])
@token_required
def get_progress(current_user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    cursor.execute('''
        SELECT * FROM weekly_progress 
        WHERE user_id = ? AND week_start_date = ?
    ''', (current_user_id, week_start))
    
    progress = cursor.fetchone()
    
    cursor.execute('''
        SELECT weekly_points_target FROM user_goals 
        WHERE user_id = ? AND is_active = 1
    ''', (current_user_id,))
    
    goal = cursor.fetchone()
    conn.close()
    
    if not progress:
        return jsonify({
            'total_points': 0,
            'meals_logged': 0,
            'target': goal['weekly_points_target'] if goal else 100,
            'week_start': str(week_start)
        }), 200
    
    return jsonify({
        'total_points': progress['total_points'],
        'meals_logged': progress['meals_logged'],
        'total_calories': progress['total_calories'],
        'target': goal['weekly_points_target'] if goal else 100,
        'week_start': str(week_start)
    }), 200

# Get user logs
@app.route('/api/logs', methods=['GET'])
@token_required
def get_logs(current_user_id):
    limit = request.args.get('limit', 10, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM food_logs 
        WHERE user_id = ? 
        ORDER BY logged_at DESC 
        LIMIT ?
    ''', (current_user_id, limit))
    
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'logs': logs}), 200

# Get user profile
@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_user_profile(current_user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, email, created_at FROM users WHERE user_id = ?', (current_user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'user_id': user['user_id'],
        'username': user['username'],
        'email': user['email'],
        'created_at': user['created_at']
    }), 200

# Update user profile
@app.route('/api/user/profile', methods=['PUT'])
@token_required
def update_user_profile(current_user_id):
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE users 
            SET username = ?, email = ?
            WHERE user_id = ?
        ''', (username, email, current_user_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'message': 'Username or email already exists'}), 409

# Change password
@app.route('/api/user/change-password', methods=['POST'])
@token_required
def change_password(current_user_id):
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE user_id = ?', (current_user_id,))
    user = cursor.fetchone()
    
    if not user or not check_password_hash(user['password_hash'], current_password):
        conn.close()
        return jsonify({'message': 'Current password is incorrect'}), 401
    
    new_password_hash = generate_password_hash(new_password)
    cursor.execute('UPDATE users SET password_hash = ? WHERE user_id = ?', (new_password_hash, current_user_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Password changed successfully'}), 200

# Serve uploaded images
@app.route('/uploads/<filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Upload profile picture
@app.route('/api/user/upload-profile-picture', methods=['POST'])
@token_required
def upload_profile_picture(current_user_id):
    if 'image' not in request.files:
        return jsonify({'message': 'No image provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    # Save image
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"profile_{current_user_id}_{timestamp}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save and resize image
    img = Image.open(file)
    img = img.resize((200, 200))
    img.save(filepath)
    
    # Update user record with profile picture path
    conn = get_db()
    cursor = conn.cursor()
    
    # First check if column exists, if not add it
    try:
        cursor.execute('UPDATE users SET profile_picture = ? WHERE user_id = ?', (filename, current_user_id))
    except sqlite3.OperationalError:
        # Column doesn't exist, add it
        cursor.execute('ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255)')
        cursor.execute('UPDATE users SET profile_picture = ? WHERE user_id = ?', (filename, current_user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Profile picture uploaded', 'filename': filename}), 200

# Get profile picture
@app.route('/api/user/profile-picture', methods=['GET'])
@token_required
def get_profile_picture(current_user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT profile_picture FROM users WHERE user_id = ?', (current_user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result['profile_picture']:
            return jsonify({'profile_picture': result['profile_picture']}), 200
    except sqlite3.OperationalError:
        # Column doesn't exist yet
        conn.close()
    
    return jsonify({'profile_picture': None}), 200

# Get user goals
@app.route('/api/user/goals', methods=['GET'])
@token_required
def get_user_goals(current_user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM user_goals 
        WHERE user_id = ? AND is_active = 1
        ORDER BY goal_id DESC LIMIT 1
    ''', (current_user_id,))
    goal = cursor.fetchone()
    conn.close()
    
    if goal:
        return jsonify({'goal': dict(goal)}), 200
    return jsonify({'goal': None}), 200

# Set/Update user goals
@app.route('/api/user/goals', methods=['POST'])
@token_required
def set_user_goals(current_user_id):
    data = request.get_json()
    goal_type = data.get('goal_type')
    weekly_points_target = data.get('weekly_points_target', 100)
    calorie_target = data.get('calorie_target', 2000)
    protein_target = data.get('protein_target', 120)
    goal_description = data.get('goal_description', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Deactivate old goals
    cursor.execute('UPDATE user_goals SET is_active = 0 WHERE user_id = ?', (current_user_id,))
    
    # Create new goal
    cursor.execute('''
        INSERT INTO user_goals 
        (user_id, goal_type, weekly_points_target, calorie_target, protein_target, start_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    ''', (current_user_id, goal_type, weekly_points_target, calorie_target, 
          protein_target, datetime.now().date()))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Goals updated successfully'}), 200

if __name__ == '__main__':
    import os
    
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    
    # Check if we're in production or development
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)