from app import db, app

# Run within application context
with app.app_context():
    db.create_all()
    print("Tables created successfully.")

