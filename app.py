from flask import Flask, render_template, request, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_items.db'
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# USDA API key
USDA_API_KEY = "I7Q7yMbYcIaMTqJotwGAkdR0VGy8flErK1aJsfbR"

@app.route('/remove_single/<int:item_index>', methods=['POST'])
def remove_single(item_index):
    """Remove a single item from the diet based on its index."""
    diet = session.get('diet', [])
    if 0 <= item_index < len(diet):  # Ensure index is within range
        diet.pop(item_index)
        session['diet'] = diet
        session['total_calories'] = sum(item['calories'] for item in diet)
        flash("Item removed from your diet.")
    return redirect(url_for('view_diet'))

@app.route('/remove_all', methods=['POST'])
def remove_all():
    """Remove all items from the diet."""
    session['diet'] = []
    session['total_calories'] = 0
    flash("All items removed from your diet.")
    return redirect(url_for('view_diet'))

    
class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    serving_size = db.Column(db.String(20), nullable=True)


def calculate_bmr(age, weight, height, gender):
    if gender == 'male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    return round(bmr)

def calculate_caloric_needs(bmr, activity_level):
    activity_factors = {
        'sedentary': 1.2,
        'lightly active': 1.375,
        'moderately active': 1.55,
        'very active': 1.725,
        'super active': 1.9,
    }
    if activity_level in activity_factors:
        return {
            'maintain': round(bmr * activity_factors[activity_level]),
            'lose_weight_slowly': round(bmr * activity_factors[activity_level] - 500),
            'lose_weight_quickly': round(bmr * activity_factors[activity_level] - 1000),
            'gain_weight_slowly': round(bmr * activity_factors[activity_level] + 500),
            'gain_weight_quickly': round(bmr * activity_factors[activity_level] + 1000),
        }
    return None

@app.route('/test_session')
def test_session():
    # Manually add an item to the diet for testing
    session['diet'] = [{'name': 'Banana', 'calories': 89}]
    session['total_calories'] = 89
    diet = session.get('diet', [])
    total_calories = session.get('total_calories', 0)
    return f"Diet: {diet}, Total Calories: {total_calories}"

@app.route('/clear_session')
def clear_session():
    session.clear()
    flash("Session cleared!")
    return redirect(url_for('test_session'))




@app.route('/search_food', methods=['GET', 'POST'])
def search_food():
    if request.method == 'POST':
        query = request.form.get('query')
        if not query:
            flash('Please enter a food name to search.')
            return redirect(url_for('search_food'))

        # Check if the item exists in the local database
        local_results = FoodItem.query.filter(FoodItem.name.ilike(f'%{query}%')).all()
        if local_results:
            return render_template('search_results.html', results=local_results, query=query)

        # If not found, query the USDA API
        headers = {'Content-Type': 'application/json'}
        params = {
            'api_key': USDA_API_KEY,
            'query': query,
            'dataType': ['Survey (FNDDS)'],
            'pageSize': 10
        }
        response = requests.get("https://api.nal.usda.gov/fdc/v1/foods/search", headers=headers, params=params)
        data = response.json()

        # Extract relevant information from the API response
        results = []
        if 'foods' in data:
            for item in data['foods']:
                food_name = item.get('description', 'N/A')
                calories = None
                serving_size = None

                # Try to get calories specifically by looking for "Energy" or "calories"
                for nutrient in item.get('foodNutrients', []):
                    if (nutrient['nutrientName'].lower() in ['energy', 'calories'] and
                        nutrient['unitName'].lower() == 'kcal'):
                        calories = nutrient.get('value', None)
                        break  # Stop once we find the calories

                # Handle serving size if available, otherwise default message
                if 'servingSize' in item and 'servingSizeUnit' in item:
                    serving_size = f"{item['servingSize']} {item['servingSizeUnit']}"
                else:
                    serving_size = "Serving size not specified"  # Default message

                # Add only if calories were found to avoid "N/A" issues
                if calories is not None:
                    results.append({
                        'name': food_name,
                        'calories': calories,
                        'serving_size': serving_size
                    })

        # Check if results are empty after filtering out items without calories
        if not results:
            flash("No foods with calorie information found. Try a different search term.", 'warning')

        return render_template('search_results.html', results=results, query=query)

    return render_template('search_food.html')




@app.route('/add_to_diet', methods=['POST'])
def add_to_diet():
    product_name = request.form.get('product_name')
    calories = request.form.get('calories', type=float)

    if not product_name or calories is None:
        flash("Invalid product information.")
        return redirect(url_for('search_food'))

    # Add to session diet list or save to local database
    diet = session.get('diet', [])
    diet.append({'name': product_name, 'calories': calories})
    session['diet'] = diet
    session['total_calories'] = sum(item['calories'] for item in diet)

    flash(f"Added {product_name} with {calories} calories to your diet.")
    return redirect(url_for('view_diet'))



@app.route('/view_diet')
def view_diet():
    diet = session.get('diet', [])
    total_calories = sum(item['calories'] for item in diet)
    return render_template('view_diet.html', diet=diet, total_calories=total_calories)

@app.route('/select_goal', methods=['GET', 'POST'])
def select_goal():
    caloric_needs = session.get('caloric_needs', None)
    if request.method == 'POST':
        goal = request.form.get('goal')
        if caloric_needs and goal in caloric_needs:
            session['calorie_goal'] = caloric_needs[goal]
            return redirect(url_for('meal_plan'))
        else:
            flash("Please select a valid goal.", 'error')
    return render_template('select_goal.html', caloric_needs=caloric_needs)

@app.route('/meal_plan', methods=['GET', 'POST'])
def meal_plan():
    calorie_goal = session.get('calorie_goal', None)
    food_items = FoodItem.query.all()  # Fetch all food items from the database
    total_calories = session.get('total_calories', 0)
    diet = session.get('diet', [])

    # Debugging prints
    print("Calorie Goal:", calorie_goal)
    print("Total Calories:", total_calories)
    print("Diet:", diet)
    print("Food Items:", [(item.name, item.calories, item.serving_size) for item in food_items])

    if request.method == 'POST':
        if 'add_to_diet' in request.form:
            selected_food_id = request.form.get('food_id')
            quantity_str = request.form.get(f'quantity-{selected_food_id}')
            unit = request.form.get(f'unit-{selected_food_id}')

            if selected_food_id and quantity_str:
                try:
                    quantity = float(quantity_str) if quantity_str else 0.0
                    food = FoodItem.query.get(int(selected_food_id))

                    if food:
                        if unit == "ounces":
                            quantity *= 28.35  # Convert ounces to grams
                        elif unit == "servings":
                            quantity = 100  # Assume each serving is 100 grams

                        calories = (quantity / 100) * food.calories
                        diet_entry = {
                            'name': food.name,
                            'quantity': quantity_str,
                            'unit': unit,
                            'calories': calories
                        }

                        diet.append(diet_entry)
                        total_calories += calories
                        session['diet'] = diet
                        session['total_calories'] = total_calories
                except ValueError:
                    flash("Please enter a valid number for quantity.", 'error')

        elif 'remove_all' in request.form:
            diet = []
            total_calories = 0
            session['diet'] = diet
            session['total_calories'] = total_calories

    return render_template(
        'meal_plan.html', 
        food_items=food_items, 
        total_calories=total_calories,
        calorie_goal=calorie_goal,
        diet=diet
    )




@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            age = int(request.form['age'])
            weight_unit = request.form['weight_unit']
            weight = float(request.form['weight'])
            gender = request.form['gender']
            unit_system = request.form['unit_system']

            if weight_unit == 'pounds':
                weight *= 0.453592

            if age <= 0 or weight <= 0:
                flash('Please enter valid positive numbers for age and weight.', 'error')
                return render_template('index.html')

            if unit_system == 'customary':
                height_feet = request.form.get('height_feet', None)
                height_inches = request.form.get('height_inches', None)

                if not height_feet or not height_inches:
                    flash('Please enter both feet and inches for height.', 'error')
                    return render_template('index.html')

                height_feet = int(height_feet)
                height_inches = int(height_inches)
                
                if height_feet < 0 or height_inches < 0 or height_inches >= 12:
                    flash('Please enter valid numbers for height.', 'error')
                    return render_template('index.html')

                height = (height_feet * 12 + height_inches) * 2.54
            else:
                height_cm = request.form.get('height_cm', None)
                if not height_cm:
                    flash('Please enter a valid height in centimeters.', 'error')
                    return render_template('index.html')

                height = float(height_cm)
                if height <= 0:
                    flash('Please enter a valid positive number for height.', 'error')
                    return render_template('index.html')

            bmr = calculate_bmr(age, weight, height, gender)
            activity_level = request.form['activity_level']
            caloric_needs = calculate_caloric_needs(bmr, activity_level)

            if caloric_needs is None:
                flash('Invalid activity level selected. Please choose a valid option.', 'error')
                return render_template('index.html')

            session['bmr'] = bmr
            session['activity_level'] = activity_level
            session['caloric_needs'] = caloric_needs

            return render_template('index.html', bmr=bmr, caloric_needs=caloric_needs,
                                   age=age, weight=weight, weight_unit=weight_unit,
                                   gender=gender, unit_system=unit_system,
                                   height_feet=height_feet if unit_system == 'customary' else None,
                                   height_inches=height_inches if unit_system == 'customary' else None,
                                   height_cm=height if unit_system == 'metric' else None,
                                   activity_level=activity_level)

        except ValueError:
            flash('Invalid input. Please enter numeric values for age, weight, and height.', 'error')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')

    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(debug=True)
