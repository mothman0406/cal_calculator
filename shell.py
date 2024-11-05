from app import db, FoodItem, populate_food_items
db.create_all()  # This should create the `food_items.db` file
populate_food_items()  # This should populate the file with sample data

