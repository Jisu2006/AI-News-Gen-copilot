import json
import logging
from flask import Flask, render_template

try:
    from flask_wtf.csrf import CSRFProtect
except ImportError:
    class CSRFProtect:
        def __init__(self, *args, **kwargs):
            pass

        def init_app(self, app):
            pass

from config import Config
from database.db import db
from routes.auth import auth
from routes.user import user
from routes.admin import admin
from routes.news import news

from models.database_models import User, News, AdminAction, OTPVerification


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CSRF Protection
    csrf = CSRFProtect(app)

    # Initialize Database
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(admin)
    app.register_blueprint(news)

    # Template Filters
    @app.template_filter("from_json")
    def from_json(value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return [value] if isinstance(value, str) else []

    # ==================================================
    # ERROR HANDLERS
    # ==================================================

    @app.errorhandler(400)
    def bad_request_error(e):
        return render_template(
            "errors/error.html",
            error_code=400,
            error_title="Bad Request",
            error_description="The request could not be processed by the server.",
            error_icon="bi-exclamation-circle"
        ), 400

    @app.errorhandler(401)
    def unauthorized_error(e):
        return render_template(
            "errors/error.html",
            error_code=401,
            error_title="Unauthorized",
            error_description="Authentication is required to access this resource.",
            error_icon="bi-lock"
        ), 401

    @app.errorhandler(403)
    def forbidden_error(e):
        return render_template(
            "errors/error.html",
            error_code=403,
            error_title="Access Forbidden",
            error_description="You do not have permission to access this page.",
            error_icon="bi-shield-x"
        ), 403

    @app.errorhandler(404)
    def not_found_error(e):
        return render_template(
            "errors/error.html",
            error_code=404,
            error_title="Page Not Found",
            error_description="The requested page or news article does not exist or is not available.",
            error_icon="bi-question-circle"
        ), 404

    @app.errorhandler(405)
    def method_not_allowed_error(e):
        return render_template(
            "errors/error.html",
            error_code=405,
            error_title="Method Not Allowed",
            error_description="The HTTP method used is not supported for this endpoint.",
            error_icon="bi-slash-circle"
        ), 405

    @app.errorhandler(413)
    def payload_too_large_error(e):
        return render_template(
            "errors/error.html",
            error_code=413,
            error_title="File Too Large",
            error_description="The uploaded file size exceeds the allowed system limit (10MB image / 100MB video).",
            error_icon="bi-file-earmark-x"
        ), 413

    @app.errorhandler(429)
    def too_many_requests_error(e):
        return render_template(
            "errors/error.html",
            error_code=429,
            error_title="Too Many Requests",
            error_description="You have made too many requests. Please wait a moment before trying again.",
            error_icon="bi-hourglass-split"
        ), 429

    @app.errorhandler(500)
    def internal_server_error(e):
        logging.error(f"Server Error 500: {e}")
        return render_template(
            "errors/error.html",
            error_code=500,
            error_title="Internal Server Error",
            error_description="An unexpected server error occurred. Our team has been notified.",
            error_icon="bi-tools"
        ), 500

    return app


app = create_app()

# Ensure database tables exist
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)