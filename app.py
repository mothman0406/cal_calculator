from flask import Flask, render_template, request

app = Flask(__name__)

# Define calorie calculation function
def calculate_bmr(gender, weight, height, age, activity_level):
    if gender == 'male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    
    # Adjust BMR based on activity level
    if activity_level == 'sedentary':
        return bmr * 1.2
    elif activity_level == 'lightly_active':
        return bmr * 1.375
    elif activity_level == 'moderately_active':
        return bmr * 1.55
    elif activity_level == 'very_active':
        return bmr * 1.725
    elif activity_level == 'extra_active':
        return bmr * 1.9

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        gender = request.form['gender']
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        age = int(request.form['age'])
        activity_level = request.form['activity_level']
        
        # Calculate BMR
        bmr = calculate_bmr(gender, weight, height, age, activity_level)
        slow_loss = bmr - 500
        quick_loss = bmr - 1000
        slow_gain = bmr + 500
        quick_gain = bmr + 1000

        return render_template('result.html', bmr=bmr, slow_loss=slow_loss, quick_loss=quick_loss, slow_gain=slow_gain, quick_gain=quick_gain)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
