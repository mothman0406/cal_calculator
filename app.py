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
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            age = int(request.form['age'])
            weight = float(request.form['weight'])
            gender = request.form['gender']
            unit_system = request.form['unit_system']

            # Input validation
            if age <= 0 or weight <= 0:
                flash('Please enter valid positive numbers for age and weight.', 'error')
                return render_template('index.html')

            if unit_system == 'customary':
                height_feet = int(request.form['height_feet'])
                height_inches = int(request.form['height_inches'])
                height = (height_feet * 12) + height_inches  # Convert height to inches
            else:  # metric
                height = float(request.form['height'])

            bmr = calculate_bmr(age, weight, height, gender)
            activity_level = request.form['activity_level']
            caloric_needs = calculate_caloric_needs(bmr, activity_level)

            return render_template('index.html', bmr=bmr, caloric_needs=caloric_needs)

        except ValueError:
            flash('Invalid input. Please enter numeric values for age, weight, and height.', 'error')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
