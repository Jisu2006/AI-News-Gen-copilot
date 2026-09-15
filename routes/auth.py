from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database.db import db
from models.database_models import User


auth = Blueprint("auth", __name__)


# ==================================================
# USER REGISTRATION
# ==================================================

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Basic validation
        if not name or not email or not password:

            flash(
                "All fields are required.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # Password validation
        if len(password) < 6:

            flash(
                "Password must be at least 6 characters.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # Check existing user
        existing_user = User.query.filter_by(
            email=email
        ).first()


        if existing_user:

            flash(
                "Email already registered.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # Hash password
        password_hash = generate_password_hash(
            password
        )


        # Create normal user
        user = User(

            name=name,

            email=email,

            password_hash=password_hash,

            role="user"

        )


        db.session.add(user)

        db.session.commit()


        flash(
            "Registration successful. Please login.",
            "success"
        )


        # Redirect to USER login
        return redirect(
            url_for("auth.user_login")
        )


    return render_template(
        "register.html"
    )


# ==================================================
# USER LOGIN
# ==================================================

@auth.route(
    "/user/login",
    methods=["GET", "POST"]
)
def user_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        # Validation
        if not email or not password:

            flash(
                "Email and password are required.",
                "error"
            )

            return redirect(
                url_for("auth.user_login")
            )


        # Find user
        user = User.query.filter_by(
            email=email
        ).first()


        # Check credentials
        if user and check_password_hash(
            user.password_hash,
            password
        ):

            # IMPORTANT:
            # User login cannot be used for admin
            if user.role != "user":

                flash(
                    "This login is only for users.",
                    "error"
                )

                return redirect(
                    url_for("auth.user_login")
                )


            # Create session
            session.clear()

            session["user_id"] = user.id

            session["user_name"] = user.name

            session["user_role"] = user.role


            # Redirect to user dashboard
            return redirect(
                url_for("user.dashboard")
            )


        flash(
            "Invalid user email or password.",
            "error"
        )

        return redirect(
            url_for("auth.user_login")
        )


    return render_template(
        "auth/user_login.html"
    )


# ==================================================
# ADMIN LOGIN
# ==================================================

@auth.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        # Validation
        if not email or not password:

            flash(
                "Email and password are required.",
                "error"
            )

            return redirect(
                url_for("auth.admin_login")
            )


        # Find user
        user = User.query.filter_by(
            email=email
        ).first()


        # Check credentials
        if user and check_password_hash(
            user.password_hash,
            password
        ):

            # IMPORTANT:
            # Admin login can only be used by admin
            if user.role != "admin":

                flash(
                    "This login is only for administrators.",
                    "error"
                )

                return redirect(
                    url_for("auth.admin_login")
                )


            # Create session
            session.clear()

            session["user_id"] = user.id

            session["user_name"] = user.name

            session["user_role"] = user.role


            # Redirect to admin dashboard
            return redirect(
                url_for("admin.dashboard")
            )


        flash(
            "Invalid admin email or password.",
            "error"
        )

        return redirect(
            url_for("auth.admin_login")
        )


    return render_template(
        "auth/admin_login.html"
    )


# ==================================================
# LOGOUT
# ==================================================

@auth.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )


    # After logout go to USER login
    return redirect(
        url_for("news.homepage")
    )