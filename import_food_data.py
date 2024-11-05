import sys
import pandas as pd
from app import db, FoodItem, app  # Import the Flask app along with db and FoodItem

# Add the directory containing 'app.py' to the Python path
sys.path.insert(0, '/Users/mohammadothman/Desktop/cal_calculator')

# Path to your CSV file
csv_file_path = '/Users/mohammadothman/Downloads/FoodData_Central_branded_food_csv_2024-04-18/branded_food.csv'

# Step 1: Preview the CSV file to understand the structure
df = pd.read_csv(csv_file_path, nrows=5)  # Only read the first 5 rows to preview
print("Preview of CSV columns:")
print(df.columns)

# Adjusted to available columns: 'short_description' as the food name, 'serving_size' as quantity
def import_food_data(filename=csv_file_path, num_rows=10):  # Limit to 10 rows for quick import
    # Load only the necessary columns and limit to the first 10 rows
    data = pd.read_csv(filename, usecols=['short_description', 'serving_size', 'serving_size_unit'], nrows=num_rows)

    # Iterate through the DataFrame and insert each row into the database
    for _, row in data.iterrows():
        # Skip rows with missing essential data
        if pd.isna(row['short_description']) or pd.isna(row['serving_size']):
            continue  # Skip this row if 'short_description' or 'serving_size' is NaN

        food_name = row['short_description']
        serving_size = f"{row['serving_size']} {row['serving_size_unit']}" if pd.notna(row['serving_size_unit']) else f"{row['serving_size']}"

        # Placeholder for calories - need confirmation of the correct column
        food = FoodItem(
            name=food_name,
            calories_per_100g=0,  # Replace 0 with the actual calories once identified
            serving_size=serving_size
        )
        db.session.add(food)
    
    # Commit all changes at once
    db.session.commit()
    print(f"Successfully imported {num_rows} rows.")

# Run the function within the application context
if __name__ == "__main__":
    with app.app_context():  # Activate the application context
        import_food_data()

