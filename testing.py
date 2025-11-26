import tensorflow as tf
import numpy as np
from PIL import Image

# Load the saved model
model = tf.keras.models.load_model('nutritional_analysis_model.keras')

# Get class names from your training
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
               'sushi', 'tacos', 'takoyaki', 'tiramisu', 'tuna_tartare',
               'waffles']

def preprocess_image(image_path):
    """Preprocess image for prediction"""
    img = Image.open(image_path).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_food(image_path, top_k=3):
    """Predict food class from image"""
    img_array = preprocess_image(image_path)
    predictions = model.predict(img_array)
    
    # Get top k predictions
    top_indices = np.argsort(predictions[0])[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        results.append({
            'class': CLASS_NAMES[idx],
            'confidence': float(predictions[0][idx])
        })
    
    return results

# Test with an image
if __name__ == "__main__":
    test_image = "C:\\Users\\warre\\Documents\\food-101\\images\\donuts\\4919.jpg"  # Replace with actual path
    predictions = predict_food(test_image)
    
    print("Top 3 Predictions:")
    for i, pred in enumerate(predictions, 1):
        print(f"{i}. {pred['class']}: {pred['confidence']*100:.2f}%")