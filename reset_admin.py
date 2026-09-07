from app import app
from database.db import db
from models.database_models import User
from werkzeug.security import generate_password_hash


ADMIN_EMAIL = "jisu@gmail.com"
NEW_PASSWORD = "Admin@12345"


with app.app_context():

    user = User.query.filter_by(
        email=ADMIN_EMAIL
    ).first()

    if not user:
        print("Admin user not found.")
    else:

        user.role = "admin"

        user.password_hash = generate_password_hash(
            NEW_PASSWORD
        )

        db.session.commit()

        print("Admin account updated successfully.")
        print("Email:", ADMIN_EMAIL)
        print("Role:", user.role)