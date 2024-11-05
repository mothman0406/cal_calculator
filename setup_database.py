from app import db, FoodItem, app

def populate_food_items():
    if FoodItem.query.count() == 0:
        sample_foods = [
            FoodItem(name='Apple', calories=52, serving_size='100g'),
            FoodItem(name='Banana', calories=96, serving_size='100g'),
            FoodItem(name='Chicken Breast', calories=165, serving_size='100g'),
            FoodItem(name='Egg', calories=155, serving_size='100g'),
            FoodItem(name='Bread', calories=265, serving_size='100g')
        ]
        db.session.bulk_save_objects(sample_foods)
        db.session.commit()
        print("Database populated with initial data.")
    else:
        print("Database already populated.")

# Create the database tables and populate initial data
with app.app_context():
    db.create_all()
    populate_food_items()
