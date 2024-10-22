from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

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
    else:
        return None  # Invalid activity level

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            age = int(request.form['age'])
            weight_unit = request.form['weight_unit']
            weight = float(request.form['weight'])
            gender = request.form['gender']
            unit_system = request.form['unit_system']

            # Convert weight to kg if the user chooses pounds
            if weight_unit == 'pounds':
                weight *= 0.453592  # Convert pounds to kilograms

            # Input validation
            if age <= 0 or weight <= 0:
                flash('Please enter valid positive numbers for age and weight.', 'error')
                return render_template('index.html')

            # Handle height based on unit system
            if unit_system == 'customary':
                height_feet = request.form.get('height_feet', None)
                height_inches = request.form.get('height_inches', None)

                # Ensure height inputs are not empty
                if not height_feet or not height_inches:
                    flash('Please enter both feet and inches for height.', 'error')
                    return render_template('index.html')

                height_feet = int(height_feet)
                height_inches = int(height_inches)
                
                if height_feet < 0 or height_inches < 0 or height_inches >= 12:
                    flash('Please enter valid numbers for height.', 'error')
                    return render_template('index.html')

                height = (height_feet * 12 + height_inches) * 2.54  # Convert height to centimeters

            else:  # metric (centimeters)
                height_cm = request.form.get('height_cm', None)

                # Ensure height in centimeters is not empty
                if not height_cm:
                    flash('Please enter a valid height in centimeters.', 'error')
                    return render_template('index.html')

                height = float(height_cm)
                if height <= 0:
                    flash('Please enter a valid positive number for height.', 'error')
                    return render_template('index.html')

            # Calculate BMR
            bmr = calculate_bmr(age, weight, height, gender)
            activity_level = request.form['activity_level']
            caloric_needs = calculate_caloric_needs(bmr, activity_level)

            if caloric_needs is None:
                flash('Invalid activity level selected. Please choose a valid option.', 'error')
                return render_template('index.html')

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
    app.run(debug=True)
