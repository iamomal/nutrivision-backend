import sqlite3

def populate_complete_nutrition_database():
    """
    Populate the database with nutritional information for all 101 food categories.
    Values are approximate per standard serving size.
    Format: (food_name, calories, protein_g, carbs_g, fat_g, serving_size, health_score, category)
    Health score: 0-100, where higher = healthier
    """
    
    complete_nutrition_data = [
        # Desserts & Sweets (Health Score: 20-40)
        ('apple_pie', 237, 2, 34, 11, '1 slice (125g)', 35, 'dessert'),
        ('baklava', 334, 5, 29, 23, '1 piece (70g)', 30, 'dessert'),
        ('beignets', 260, 5, 35, 11, '3 pieces', 25, 'dessert'),
        ('bread_pudding', 270, 6, 38, 10, '1 cup', 35, 'dessert'),
        ('cannoli', 380, 8, 42, 19, '1 cannoli', 30, 'dessert'),
        ('carrot_cake', 415, 5, 56, 19, '1 slice', 35, 'dessert'),
        ('cheesecake', 321, 6, 26, 23, '1 slice', 25, 'dessert'),
        ('chocolate_cake', 352, 5, 50, 14, '1 slice', 30, 'dessert'),
        ('chocolate_mousse', 268, 4, 22, 19, '1 cup', 25, 'dessert'),
        ('churros', 312, 4, 42, 15, '4 pieces', 25, 'dessert'),
        ('creme_brulee', 294, 7, 30, 15, '1 serving', 30, 'dessert'),
        ('cup_cakes', 305, 3, 45, 13, '1 cupcake', 25, 'dessert'),
        ('donuts', 292, 4, 35, 15, '1 donut', 20, 'dessert'),
        ('frozen_yogurt', 127, 4, 24, 2, '1 cup', 55, 'dessert'),
        ('ice_cream', 207, 4, 24, 11, '1 cup', 30, 'dessert'),
        ('macarons', 90, 2, 13, 4, '1 macaron', 35, 'dessert'),
        ('panna_cotta', 301, 4, 27, 20, '1 serving', 30, 'dessert'),
        ('red_velvet_cake', 390, 5, 52, 18, '1 slice', 25, 'dessert'),
        ('strawberry_shortcake', 315, 4, 44, 14, '1 serving', 40, 'dessert'),
        ('tiramisu', 240, 5, 29, 11, '1 serving', 35, 'dessert'),
        
        # Breakfast Items (Health Score: 40-70)
        ('breakfast_burrito', 450, 20, 42, 21, '1 burrito', 60, 'breakfast'),
        ('croque_madame', 512, 28, 35, 28, '1 sandwich', 50, 'breakfast'),
        ('eggs_benedict', 450, 20, 30, 25, '1 serving', 55, 'breakfast'),
        ('french_toast', 280, 10, 35, 11, '2 slices', 45, 'breakfast'),
        ('huevos_rancheros', 380, 18, 35, 18, '1 serving', 65, 'breakfast'),
        ('omelette', 220, 18, 3, 16, '3 eggs', 70, 'breakfast'),
        ('pancakes', 227, 6, 36, 7, '3 pancakes', 45, 'breakfast'),
        ('waffles', 291, 7, 37, 13, '2 waffles', 45, 'breakfast'),
        
        # Salads (Health Score: 70-90)
        ('beet_salad', 180, 4, 18, 11, '1 bowl', 85, 'salad'),
        ('caesar_salad', 184, 6, 8, 15, '1 bowl', 65, 'salad'),
        ('caprese_salad', 220, 11, 8, 16, '1 serving', 80, 'salad'),
        ('greek_salad', 150, 4, 8, 12, '1 bowl', 85, 'salad'),
        ('seaweed_salad', 70, 2, 10, 3, '1 cup', 90, 'salad'),
        
        # Protein-Rich Mains (Health Score: 70-95)
        ('baby_back_ribs', 361, 27, 0, 28, '4 oz', 55, 'main'),
        ('beef_carpaccio', 186, 22, 2, 10, '4 oz', 75, 'main'),
        ('beef_tartare', 220, 20, 3, 14, '4 oz', 70, 'main'),
        ('chicken_curry', 350, 25, 20, 18, '1 cup', 70, 'main'),
        ('chicken_quesadilla', 450, 25, 38, 22, '1 quesadilla', 60, 'main'),
        ('chicken_wings', 290, 27, 0, 20, '4 wings', 50, 'main'),
        ('crab_cakes', 340, 18, 22, 20, '2 cakes', 65, 'main'),
        ('filet_mignon', 278, 40, 0, 13, '6 oz', 85, 'main'),
        ('foie_gras', 462, 11, 1, 44, '2 oz', 40, 'main'),
        ('grilled_salmon', 280, 39, 0, 13, '6 oz', 95, 'main'),
        ('peking_duck', 337, 19, 0, 28, '4 oz', 60, 'main'),
        ('pork_chop', 231, 39, 0, 7, '6 oz', 75, 'main'),
        ('prime_rib', 338, 36, 0, 21, '6 oz', 70, 'main'),
        ('scallops', 137, 24, 6, 1, '6 oz', 90, 'main'),
        ('steak', 271, 43, 0, 10, '6 oz', 80, 'main'),
        ('tuna_tartare', 185, 26, 2, 8, '4 oz', 85, 'main'),
        
        # Asian Dishes (Health Score: 60-80)
        ('bibimbap', 490, 20, 62, 18, '1 bowl', 75, 'main'),
        ('dumplings', 280, 12, 35, 10, '6 dumplings', 65, 'main'),
        ('edamame', 120, 11, 10, 5, '1 cup', 90, 'appetizer'),
        ('fried_rice', 333, 8, 50, 11, '1 cup', 55, 'main'),
        ('gyoza', 250, 10, 30, 9, '6 pieces', 65, 'appetizer'),
        ('hot_and_sour_soup', 112, 7, 12, 4, '1 bowl', 70, 'soup'),
        ('miso_soup', 84, 6, 8, 3, '1 bowl', 85, 'soup'),
        ('pad_thai', 380, 15, 50, 12, '1 plate', 65, 'main'),
        ('pho', 350, 20, 45, 8, '1 bowl', 75, 'main'),
        ('ramen', 436, 19, 54, 15, '1 bowl', 60, 'main'),
        ('sashimi', 130, 25, 0, 3, '6 pieces', 95, 'main'),
        ('spring_rolls', 140, 4, 20, 5, '2 rolls', 70, 'appetizer'),
        ('sushi', 200, 9, 28, 5, '6 pieces', 75, 'main'),
        ('takoyaki', 180, 8, 22, 7, '5 balls', 60, 'snack'),
        
        # European Dishes (Health Score: 50-70)
        ('bruschetta', 140, 4, 18, 6, '2 pieces', 70, 'appetizer'),
        ('escargots', 180, 16, 4, 12, '6 snails', 65, 'appetizer'),
        ('gnocchi', 250, 6, 45, 4, '1 cup', 60, 'main'),
        ('lasagna', 360, 18, 35, 16, '1 serving', 60, 'main'),
        ('paella', 425, 25, 50, 13, '1 serving', 70, 'main'),
        ('ravioli', 350, 14, 42, 13, '1 cup', 60, 'main'),
        ('risotto', 380, 8, 55, 13, '1 cup', 55, 'main'),
        ('spaghetti_bolognese', 400, 22, 50, 12, '1 plate', 65, 'main'),
        ('spaghetti_carbonara', 480, 20, 52, 22, '1 plate', 55, 'main'),
        
        # French Dishes (Health Score: 50-70)
        ('clam_chowder', 235, 12, 20, 13, '1 bowl', 60, 'soup'),
        ('french_onion_soup', 160, 8, 15, 8, '1 bowl', 65, 'soup'),
        ('lobster_bisque', 260, 11, 14, 18, '1 bowl', 60, 'soup'),
        ('mussels', 172, 24, 7, 4, '6 oz', 85, 'main'),
        ('oysters', 57, 6, 5, 2, '6 oysters', 80, 'appetizer'),
        
        # Sandwiches & Fast Food (Health Score: 40-60)
        ('club_sandwich', 590, 30, 50, 28, '1 sandwich', 55, 'main'),
        ('fish_and_chips', 585, 28, 52, 30, '1 serving', 40, 'main'),
        ('grilled_cheese_sandwich', 440, 18, 40, 24, '1 sandwich', 45, 'main'),
        ('hamburger', 354, 20, 30, 17, '1 burger', 50, 'main'),
        ('hot_dog', 314, 12, 24, 18, '1 hot dog', 35, 'main'),
        ('lobster_roll_sandwich', 436, 25, 42, 18, '1 roll', 65, 'main'),
        ('pulled_pork_sandwich', 415, 35, 38, 13, '1 sandwich', 60, 'main'),
        
        # Snacks & Sides (Health Score: 30-60)
        ('cheese_plate', 340, 22, 6, 26, '1 serving', 55, 'appetizer'),
        ('deviled_eggs', 124, 6, 1, 10, '2 halves', 60, 'appetizer'),
        ('falafel', 333, 13, 32, 18, '5 balls', 70, 'main'),
        ('french_fries', 312, 4, 41, 15, '1 serving', 35, 'side'),
        ('fried_calamari', 295, 15, 18, 18, '1 cup', 50, 'appetizer'),
        ('garlic_bread', 186, 4, 21, 9, '2 slices', 40, 'side'),
        ('guacamole', 150, 2, 8, 14, '1/2 cup', 85, 'dip'),
        ('hummus', 166, 8, 14, 10, '1/2 cup', 80, 'dip'),
        ('macaroni_and_cheese', 310, 11, 36, 13, '1 cup', 45, 'main'),
        ('nachos', 346, 9, 36, 19, '1 serving', 40, 'snack'),
        ('onion_rings', 276, 4, 31, 16, '8 rings', 30, 'side'),
        ('poutine', 510, 12, 54, 28, '1 serving', 35, 'main'),
        ('samosa', 252, 5, 28, 13, '1 samosa', 50, 'snack'),
        ('tacos', 226, 13, 18, 12, '2 tacos', 65, 'main'),
        
        # Southern/Comfort Food (Health Score: 45-65)
        ('ceviche', 140, 18, 10, 4, '1 cup', 85, 'appetizer'),
        ('pizza', 285, 12, 36, 10, '2 slices', 45, 'main'),
        ('shrimp_and_grits', 390, 24, 42, 14, '1 serving', 65, 'main'),
    ]
    
    conn = sqlite3.connect('nutrition_app.db')
    cursor = conn.cursor()
    
    # Insert or replace all nutrition data
    cursor.executemany('''
        INSERT OR REPLACE INTO food_nutrition 
        (food_name, calories, protein, carbs, fat, serving_size, health_score, category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', complete_nutrition_data)
    
    conn.commit()
    
    # Verify insertion
    cursor.execute('SELECT COUNT(*) FROM food_nutrition')
    count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✓ Successfully populated database with {count} food items!")
    print(f"✓ Nutritional data is now complete for all Food-101 categories")
    
    return count

if __name__ == "__main__":
    populate_complete_nutrition_database()