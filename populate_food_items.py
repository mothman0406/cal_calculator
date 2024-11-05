from app import db, FoodItem, app

def populate_food_items():
    sample_foods = [
        {'name': 'Apple', 'calories': 95, 'serving_size': '1 medium'},
        {'name': 'Banana', 'calories': 105, 'serving_size': '1 medium'},
        {'name': 'Chicken Breast', 'calories': 165, 'serving_size': '3 oz'},
        {'name': 'Egg', 'calories': 70, 'serving_size': '1 large'},
        {'name': 'Bread', 'calories': 80, 'serving_size': '1 slice'}
    ]
    for food in sample_foods:
        item = FoodItem(name=food['name'], calories=food['calories'], serving_size=food['serving_size'])
        db.session.add(item)
    db.session.commit()
    print("Database populated with sample food items.")

# Run the function in an application context
if __name__ == "__main__":
    with app.app_context():
        populate_food_items()

