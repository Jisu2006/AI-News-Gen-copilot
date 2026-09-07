from flask import Flask

from config import Config
from database.db import db
from routes.auth import auth
from routes.user import user
from routes.admin import admin
from routes.news import news

from flask_wtf.csrf import CSRFProtect

import json

from models.database_models import User, News, AdminAction


app = Flask(__name__)

# Load application configuration
app.config.from_object(Config)


# Enable CSRF Protection
csrf = CSRFProtect(app)


@app.template_filter("from_json")
def from_json(value):
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []


# Initialize database
db.init_app(app)


# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(user)
app.register_blueprint(admin)
app.register_blueprint(news)


# Create database tables
with app.app_context():
    db.create_all()


@app.route("/")
def home():

    try:
        db.session.execute(db.text("SELECT 1"))

        return "Welcome to AI-NewsGen Copilot - MySQL Connected!"

    except Exception as e:

        return f"MySQL Connection Failed: {e}"


if __name__ == "__main__":
    app.run(debug=True)