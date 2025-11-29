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
from database import create_database
from nutrition_data import populate_complete_nutrition_database
import psycopg2
from psycopg2.extras import RealDictCursor

# Auto-initialize PostgreSQL tables if they don't exist
if os.environ.get('DATABASE_URL'):
    try:
        from init_db import init_database
        init_database()
    except:
        pass  # Tables already exist

# Initialize database if it doesn't exist
if not os.path.exists('nutrition_app.db'):
    print("Database not found. Creating database...")
    create_database()
    populate_complete_nutrition_database()
    print("Database initialization complete!")

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://nutrivisionincomplete.netlify.app",
            "http://localhost:3000",  # For local development
            "http://localhost:5173"   # If using Vite locally
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load model lazily to avoid memory issues
model = None

def get_model():
    global model
    if model is None:
        print("Loading model...")
        model = tf.keras.models.load_model('nutritional_analysis_model.h5')
        print("Model loaded successfully!")
    return model

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
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Production: PostgreSQL
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    else:
        # Development: SQLite
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
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('SELECT user_id FROM users WHERE username = %s OR email = %s', (username, email))
    else:
        # SQLite
        cursor.execute('SELECT user_id FROM users WHERE username = ? OR email = ?', (username, email))
    
    if cursor.fetchone():
        conn.close()
        return jsonify({'message': 'User already exists'}), 409
    
    # Create user
    password_hash = generate_password_hash(password)
    
    # Use a single transaction for both inserts
    try:
        if hasattr(cursor, 'execute'):
            # PostgreSQL with RETURNING
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s) RETURNING user_id
            ''', (username, email, password_hash))
            result = cursor.fetchone()
            user_id = result['user_id'] if result else None
        else:
            # SQLite
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            user_id = cursor.lastrowid
        
        if not user_id:
            conn.rollback()
            return jsonify({'message': 'Registration failed'}), 500
        
        # Create default goal
        if hasattr(cursor, 'execute'):
            # PostgreSQL
            cursor.execute('''
                INSERT INTO user_goals (user_id, weekly_points_target, start_date)
                VALUES (%s, 100, CURRENT_DATE)
            ''', (user_id,))
        else:
            # SQLite
            cursor.execute('''
                INSERT INTO user_goals (user_id, weekly_points_target, start_date)
                VALUES (?, 100, date('now'))
            ''', (user_id,))
        
        conn.commit()
        
        # Generate token immediately after creation
        token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user_id': user_id,
            'username': username
        }), 201
        
    except Exception as e:
        conn.rollback()
        return jsonify({'message': 'Registration failed'}), 500
    finally:
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('username')  # Can be username or email
    password = data.get('password')
    
    if not identifier or not password:
        return jsonify({'message': 'Missing credentials'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if identifier is username or email
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (identifier, identifier))
    else:
        # SQLite
        cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (identifier, identifier))
    
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({'message': 'Invalid username or email'}), 401
    
    if not check_password_hash(user['password_hash'], password):
        conn.close()
        return jsonify({'message': 'Invalid password'}), 401
    
    # Update last login
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('UPDATE users SET last_login = %s WHERE user_id = %s', 
                       (datetime.now(), user['user_id']))
    else:
        # SQLite
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
    predictions = get_model().predict(img_array)
    top_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][top_idx])
    food_name = CLASS_NAMES[top_idx]
    
    # Get nutrition info
    conn = get_db()
    cursor = conn.cursor()
    
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('SELECT * FROM food_nutrition WHERE food_name = %s', (food_name,))
    else:
        # SQLite
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
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT goal_type FROM user_goals 
            WHERE user_id = %s AND is_active = 1
            ORDER BY goal_id DESC LIMIT 1
        ''', (current_user_id,))
    else:
        # SQLite
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
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            INSERT INTO food_logs 
            (user_id, food_name, confidence_score, image_path, meal_type, 
             calories, protein, carbs, fat, points_awarded)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (current_user_id, food_name, confidence, filename, meal_type,
              nutrition_data['calories'], nutrition_data['protein'], 
              nutrition_data['carbs'], nutrition_data['fat'], points))
    else:
        # SQLite
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
    
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            INSERT INTO weekly_progress 
            (user_id, week_start_date, week_end_date, total_points, meals_logged,
             total_calories, total_protein, total_carbs, total_fat)
            VALUES (%s, %s, %s, %s, 1, %s, %s, %s, %s)
            ON CONFLICT(user_id, week_start_date) DO UPDATE SET
                total_points = weekly_progress.total_points + %s,
                meals_logged = weekly_progress.meals_logged + 1,
                total_calories = weekly_progress.total_calories + %s,
                total_protein = weekly_progress.total_protein + %s,
                total_carbs = weekly_progress.total_carbs + %s,
                total_fat = weekly_progress.total_fat + %s
        ''', (user_id, week_start, week_end, points,
              nutrition['calories'], nutrition['protein'], nutrition['carbs'], nutrition['fat'],
              points, nutrition['calories'], nutrition['protein'], nutrition['carbs'], nutrition['fat']))
    else:
        # SQLite
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
    
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT * FROM weekly_progress 
            WHERE user_id = %s AND week_start_date = %s
        ''', (current_user_id, week_start))
    else:
        # SQLite
        cursor.execute('''
            SELECT * FROM weekly_progress 
            WHERE user_id = ? AND week_start_date = ?
        ''', (current_user_id, week_start))
    
    progress = cursor.fetchone()
    
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT weekly_points_target FROM user_goals 
            WHERE user_id = %s AND is_active = 1
        ''', (current_user_id,))
    else:
        # SQLite
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
    
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT * FROM food_logs 
            WHERE user_id = %s 
            ORDER BY logged_at DESC 
            LIMIT %s
        ''', (current_user_id, limit))
    else:
        # SQLite
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
    
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('SELECT user_id, username, email, created_at FROM users WHERE user_id = %s', (current_user_id,))
    else:
        # SQLite
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
        if hasattr(cursor, 'execute'):
            # PostgreSQL
            cursor.execute('''
                UPDATE users 
                SET username = %s, email = %s
                WHERE user_id = %s
            ''', (username, email, current_user_id))
        else:
            # SQLite
            cursor.execute('''
                UPDATE users 
                SET username = ?, email = ?
                WHERE user_id = ?
            ''', (username, email, current_user_id))
        
        conn.commit()
        conn.close()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
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
    
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('SELECT password_hash FROM users WHERE user_id = %s', (current_user_id,))
    else:
        # SQLite
        cursor.execute('SELECT password_hash FROM users WHERE user_id = ?', (current_user_id,))
    
    user = cursor.fetchone()
    
    if not user or not check_password_hash(user['password_hash'], current_password):
        conn.close()
        return jsonify({'message': 'Current password is incorrect'}), 401
    
    new_password_hash = generate_password_hash(new_password)
    
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('UPDATE users SET password_hash = %s WHERE user_id = %s', (new_password_hash, current_user_id))
    else:
        # SQLite
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
        if hasattr(cursor, 'execute'):
            # PostgreSQL
            cursor.execute('UPDATE users SET profile_picture = %s WHERE user_id = %s', (filename, current_user_id))
        else:
            # SQLite
            cursor.execute('UPDATE users SET profile_picture = ? WHERE user_id = ?', (filename, current_user_id))
    except Exception as e:
        # Column doesn't exist, add it
        if hasattr(cursor, 'execute'):
            # PostgreSQL
            cursor.execute('ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255)')
            cursor.execute('UPDATE users SET profile_picture = %s WHERE user_id = %s', (filename, current_user_id))
        else:
            # SQLite
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
        if hasattr(cursor, 'execute'):
            # PostgreSQL
            cursor.execute('SELECT profile_picture FROM users WHERE user_id = %s', (current_user_id,))
        else:
            # SQLite
            cursor.execute('SELECT profile_picture FROM users WHERE user_id = ?', (current_user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result['profile_picture']:
            return jsonify({'profile_picture': result['profile_picture']}), 200
    except Exception as e:
        # Column doesn't exist yet
        conn.close()
    
    return jsonify({'profile_picture': None}), 200

# Get user goals
@app.route('/api/user/goals', methods=['GET'])
@token_required
def get_user_goals(current_user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT * FROM user_goals 
            WHERE user_id = %s AND is_active = 1
            ORDER BY goal_id DESC LIMIT 1
        ''', (current_user_id,))
    else:
        # SQLite
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
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('UPDATE user_goals SET is_active = 0 WHERE user_id = %s', (current_user_id,))
    else:
        # SQLite
        cursor.execute('UPDATE user_goals SET is_active = 0 WHERE user_id = ?', (current_user_id,))
    
    # Create new goal
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            INSERT INTO user_goals 
            (user_id, goal_type, weekly_points_target, calorie_target, protein_target, start_date, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
        ''', (current_user_id, goal_type, weekly_points_target, calorie_target, 
              protein_target, datetime.now().date()))
    else:
        # SQLite
        cursor.execute('''
            INSERT INTO user_goals 
            (user_id, goal_type, weekly_points_target, calorie_target, protein_target, start_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (current_user_id, goal_type, weekly_points_target, calorie_target, 
              protein_target, datetime.now().date()))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Goals updated successfully'}), 200

# Add this helper function for level calculation
def calculate_user_level(total_points):
    """Calculate user level based on total points"""
    # Level progression: 0→1(100pts), 1→2(250pts), 2→3(500pts), etc.
    level_thresholds = [0, 100, 250, 500, 1000, 2000, 3500, 5500, 8000, 11000, 15000]
    
    for level, threshold in enumerate(level_thresholds):
        if total_points < threshold:
            return {
                'level': level,
                'current_points': total_points,
                'points_for_level': level_thresholds[level - 1] if level > 0 else 0,
                'points_to_next': threshold - total_points if level < len(level_thresholds) else 0,
                'next_level_points': threshold if level < len(level_thresholds) else None
            }
    
    # Max level reached
    return {
        'level': len(level_thresholds),
        'current_points': total_points,
        'points_for_level': level_thresholds[-1],
        'points_to_next': 0,
        'next_level_points': None
    }

# Add achievement checking function
def check_and_award_achievements(user_id):
    """Check if user has earned any new achievements"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get user's meal streak
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT COUNT(DISTINCT DATE(logged_at)) as streak_days
            FROM food_logs
            WHERE user_id = %s
            AND DATE(logged_at) >= CURRENT_DATE - INTERVAL '7 days'
        ''', (user_id,))
    else:
        # SQLite
        cursor.execute('''
            SELECT COUNT(DISTINCT DATE(logged_at)) as streak_days
            FROM food_logs
            WHERE user_id = ?
            AND DATE(logged_at) >= DATE('now', '-7 days')
        ''', (user_id,))
    
    streak_result = cursor.fetchone()
    streak_days = streak_result['streak_days'] if streak_result else 0
    
    # Get macro stats
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT 
                SUM(protein) as total_protein,
                SUM(carbs) as total_carbs,
                SUM(fat) as total_fat,
                COUNT(*) as total_meals
            FROM food_logs
            WHERE user_id = %s
        ''', (user_id,))
    else:
        # SQLite
        cursor.execute('''
            SELECT 
                SUM(protein) as total_protein,
                SUM(carbs) as total_carbs,
                SUM(fat) as total_fat,
                COUNT(*) as total_meals
            FROM food_logs
            WHERE user_id = ?
        ''', (user_id,))
    
    macro_stats = cursor.fetchone()
    
    # Define achievements
    achievements = []
    
    # Streak achievements
    if streak_days >= 7:
        achievements.append({
            'id': 'streak_7',
            'name': 'Week Warrior',
            'description': '7-day logging streak',
            'points': 50,
            'icon': '🔥'
        })
    if streak_days >= 21:
        achievements.append({
            'id': 'streak_21',
            'name': 'Consistency King',
            'description': '21-day logging streak',
            'points': 150,
            'icon': '👑'
        })
    if streak_days >= 42:
        achievements.append({
            'id': 'streak_42',
            'name': 'Habit Master',
            'description': '42-day logging streak',
            'points': 300,
            'icon': '🏆'
        })
    
    # Protein achievements
    if macro_stats and macro_stats['total_protein']:
        if macro_stats['total_protein'] > 500:
            achievements.append({
                'id': 'protein_500',
                'name': 'Protein Rookie',
                'description': '500g total protein logged',
                'points': 30,
                'icon': '💪'
            })
        if macro_stats['total_protein'] > 2000:
            achievements.append({
                'id': 'protein_2000',
                'name': 'Protein Pro',
                'description': '2000g total protein logged',
                'points': 100,
                'icon': '🥩'
            })
    
    # Meal count achievements
    if macro_stats and macro_stats['total_meals']:
        if macro_stats['total_meals'] >= 10:
            achievements.append({
                'id': 'meals_10',
                'name': 'Getting Started',
                'description': '10 meals logged',
                'points': 20,
                'icon': '🍽️'
            })
        if macro_stats['total_meals'] >= 50:
            achievements.append({
                'id': 'meals_50',
                'name': 'Dedicated Logger',
                'description': '50 meals logged',
                'points': 75,
                'icon': '📊'
            })
        if macro_stats['total_meals'] >= 100:
            achievements.append({
                'id': 'meals_100',
                'name': 'Century Club',
                'description': '100 meals logged',
                'points': 200,
                'icon': '🎯'
            })
    
    # Check which achievements are new
    new_achievements = []
    for achievement in achievements:
        if hasattr(cursor, 'execute'):
            # PostgreSQL
            cursor.execute('''
                SELECT * FROM user_achievements 
                WHERE user_id = %s AND achievement_id = %s
            ''', (user_id, achievement['id']))
        else:
            # SQLite
            cursor.execute('''
                SELECT * FROM user_achievements 
                WHERE user_id = ? AND achievement_id = ?
            ''', (user_id, achievement['id']))
        
        if not cursor.fetchone():
            # Award new achievement
            if hasattr(cursor, 'execute'):
                # PostgreSQL
                cursor.execute('''
                    INSERT INTO user_achievements (user_id, achievement_id, earned_at, points_awarded)
                    VALUES (%s, %s, %s, %s)
                ''', (user_id, achievement['id'], datetime.now(), achievement['points']))
            else:
                # SQLite
                cursor.execute('''
                    INSERT INTO user_achievements (user_id, achievement_id, earned_at, points_awarded)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, achievement['id'], datetime.now(), achievement['points']))
            new_achievements.append(achievement)
    
    conn.commit()
    conn.close()
    
    return new_achievements

# New endpoint: Get dashboard stats
@app.route('/api/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats(current_user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    # Get total lifetime points
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT 
                COALESCE(SUM(points_awarded), 0) as total_meal_points
            FROM food_logs
            WHERE user_id = %s
        ''', (current_user_id,))
    else:
        # SQLite
        cursor.execute('''
            SELECT 
                COALESCE(SUM(points_awarded), 0) as total_meal_points
            FROM food_logs
            WHERE user_id = ?
        ''', (current_user_id,))
    
    meal_points = cursor.fetchone()['total_meal_points']
    
    # Get achievement points
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT COALESCE(SUM(points_awarded), 0) as total_achievement_points
            FROM user_achievements
            WHERE user_id = %s
        ''', (current_user_id,))
    else:
        # SQLite
        cursor.execute('''
            SELECT COALESCE(SUM(points_awarded), 0) as total_achievement_points
            FROM user_achievements
            WHERE user_id = ?
        ''', (current_user_id,))
    
    achievement_points = cursor.fetchone()['total_achievement_points']
    
    total_points = meal_points + achievement_points
    
    # Calculate level
    level_info = calculate_user_level(total_points)
    
    # Get today's nutrition totals
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT 
                COALESCE(SUM(calories), 0) as today_calories,
                COALESCE(SUM(protein), 0) as today_protein,
                COALESCE(SUM(carbs), 0) as today_carbs,
                COALESCE(SUM(fat), 0) as today_fat
            FROM food_logs
            WHERE user_id = %s AND DATE(logged_at) = CURRENT_DATE
        ''', (current_user_id,))
    else:
        # SQLite
        cursor.execute('''
            SELECT 
                COALESCE(SUM(calories), 0) as today_calories,
                COALESCE(SUM(protein), 0) as today_protein,
                COALESCE(SUM(carbs), 0) as today_carbs,
                COALESCE(SUM(fat), 0) as today_fat
            FROM food_logs
            WHERE user_id = ? AND DATE(logged_at) = DATE('now')
        ''', (current_user_id,))
    
    today_nutrition = cursor.fetchone()
    
    # Get user's goals
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT calorie_target, protein_target 
            FROM user_goals 
            WHERE user_id = %s AND is_active = 1
        ''', (current_user_id,))
    else:
        # SQLite
        cursor.execute('''
            SELECT calorie_target, protein_target 
            FROM user_goals 
            WHERE user_id = ? AND is_active = 1
        ''', (current_user_id,))
    
    goals = cursor.fetchone()
    conn.close()
    
    return jsonify({
        'level': level_info,
        'today_nutrition': {
            'calories': today_nutrition['today_calories'],
            'protein': today_nutrition['today_protein'],
            'carbs': today_nutrition['today_carbs'],
            'fat': today_nutrition['today_fat']
        },
        'goals': {
            'calorie_target': goals['calorie_target'] if goals else 2000,
            'protein_target': goals['protein_target'] if goals else 120
        }
    }), 200

# New endpoint: Get points history
@app.route('/api/dashboard/points-history', methods=['GET'])
@token_required
def get_points_history(current_user_id):
    days = request.args.get('days', 7, type=int)  # 7, 15, or 30
    
    conn = get_db()
    cursor = conn.cursor()
    
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT 
                DATE(logged_at) as date,
                SUM(points_awarded) as total_points
            FROM food_logs
            WHERE user_id = %s 
            AND DATE(logged_at) >= CURRENT_DATE - INTERVAL %s DAYS
            GROUP BY DATE(logged_at)
            ORDER BY date ASC
        ''', (current_user_id, days))
    else:
        # SQLite
        cursor.execute('''
            SELECT 
                DATE(logged_at) as date,
                SUM(points_awarded) as total_points
            FROM food_logs
            WHERE user_id = ? 
            AND DATE(logged_at) >= DATE('now', ? || ' days')
            GROUP BY DATE(logged_at)
            ORDER BY date ASC
        ''', (current_user_id, -days))
    
    history = [{'date': row['date'], 'points': row['total_points']} for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'points_history': history}), 200

# New endpoint: Get macro ratios over time
@app.route('/api/dashboard/macro-ratios', methods=['GET'])
@token_required
def get_macro_ratios(current_user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    # Get lifetime macro totals
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT 
                COALESCE(SUM(protein), 0) as total_protein,
                COALESCE(SUM(carbs), 0) as total_carbs,
                COALESCE(SUM(fat), 0) as total_fat
            FROM food_logs
            WHERE user_id = %s
        ''', (current_user_id,))
    else:
        # SQLite
        cursor.execute('''
            SELECT 
                COALESCE(SUM(protein), 0) as total_protein,
                COALESCE(SUM(carbs), 0) as total_carbs,
                COALESCE(SUM(fat), 0) as total_fat
            FROM food_logs
            WHERE user_id = ?
        ''', (current_user_id,))
    
    macros = cursor.fetchone()
    conn.close()
    
    total = macros['total_protein'] + macros['total_carbs'] + macros['total_fat']
    
    if total == 0:
        return jsonify({
            'protein_percentage': 0,
            'carbs_percentage': 0,
            'fat_percentage': 0
        }), 200
    
    return jsonify({
        'protein_percentage': round((macros['total_protein'] / total) * 100, 1),
        'carbs_percentage': round((macros['total_carbs'] / total) * 100, 1),
        'fat_percentage': round((macros['total_fat'] / total) * 100, 1)
    }), 200

# New endpoint: Get top food categories
@app.route('/api/dashboard/top-categories', methods=['GET'])
@token_required
def get_top_categories(current_user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT 
                food_name,
                COUNT(*) as count
            FROM food_logs
            WHERE user_id = %s
            GROUP BY food_name
            ORDER BY count DESC
            LIMIT 5
        ''', (current_user_id,))
    else:
        # SQLite
        cursor.execute('''
            SELECT 
                food_name,
                COUNT(*) as count
            FROM food_logs
            WHERE user_id = ?
            GROUP BY food_name
            ORDER BY count DESC
            LIMIT 5
        ''', (current_user_id,))
    
    categories = [{'name': row['food_name'].replace('_', ' ').title(), 'count': row['count']} 
                  for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'top_categories': categories}), 200

# New endpoint: Get user achievements
@app.route('/api/user/achievements', methods=['GET'])
@token_required
def get_user_achievements(current_user_id):
    # Check for new achievements first
    new_achievements = check_and_award_achievements(current_user_id)
    
    conn = get_db()
    cursor = conn.cursor()
    
    if hasattr(cursor, 'execute'):
        # PostgreSQL
        cursor.execute('''
            SELECT * FROM user_achievements
            WHERE user_id = %s
            ORDER BY earned_at DESC
        ''', (current_user_id,))
    else:
        # SQLite
        cursor.execute('''
            SELECT * FROM user_achievements
            WHERE user_id = ?
            ORDER BY earned_at DESC
        ''', (current_user_id,))
    
    achievements = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'achievements': achievements,
        'new_achievements': new_achievements
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200   

if __name__ == '__main__':
    import os
    
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    
    # Check if we're in production or development
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)