from urllib.parse import urlparse, urljoin

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from repositories.user_repository import (
    create_user,
    find_user_by_email,
    verify_user_email,
    update_registration_details,
)

from services.otp_service import (
    generate_and_send_otp,
    verify_otp,
)


auth = Blueprint(
    "auth",
    __name__
)


# ============================================================
# SAFE REDIRECT VALIDATION
# ============================================================

def is_safe_url(target: str) -> bool:
    """
    Validate that redirect target is on the same host.
    """

    if not target:
        return False

    ref_url = urlparse(
        request.host_url
    )

    test_url = urlparse(
        urljoin(
            request.host_url,
            target
        )
    )

    return (
        test_url.scheme in ("http", "https")
        and
        ref_url.netloc == test_url.netloc
    )


# ============================================================
# USER REGISTRATION
# ============================================================

@auth.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if not name or not email or not password:
            flash(
                "All fields are required.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        if (
            "@" not in email
            or "." not in email
        ):
            flash(
                "Please enter a valid email address.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        if len(password) < 6:
            flash(
                "Password must be at least 6 characters.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        # ----------------------------------------------------
        # Find existing user in MongoDB
        # ----------------------------------------------------

        existing_user = find_user_by_email(
            email
        )

        if existing_user:

            if existing_user.get(
                "is_verified",
                False
            ):

                flash(
                    "Email already registered. Please login.",
                    "error"
                )

                return redirect(
                    url_for("auth.user_login")
                )

            # ------------------------------------------------
            # Existing but unverified
            # ------------------------------------------------

            password_hash = generate_password_hash(
                password
            )

            updated_user = update_registration_details(
                email=email,
                name=name,
                password_hash=password_hash,
            )

            if not updated_user:

                flash(
                    "Unable to update your pending registration.",
                    "error"
                )

                return redirect(
                    url_for("auth.register")
                )

            success, message = generate_and_send_otp(
                email,
                "registration",
                name
            )

            if not success:

                flash(
                    message,
                    "error"
                )

                return redirect(
                    url_for("auth.register")
                )

            session[
                "pending_verification_email"
            ] = email

            flash(
                "Your previous registration was pending verification. "
                "A new OTP has been sent.",
                "success"
            )

            return redirect(
                url_for("auth.verify_otp")
            )

        # ----------------------------------------------------
        # Create new MongoDB user
        # ----------------------------------------------------

        password_hash = generate_password_hash(
            password
        )

        try:

            create_user(
                name=name,
                email=email,
                password_hash=password_hash,
                role="user",
                is_verified=False,
            )

        except Exception as error:

            # Duplicate email race-condition protection
            if "duplicate key" in str(error).lower():

                flash(
                    "Email is already registered.",
                    "error"
                )

                return redirect(
                    url_for("auth.user_login")
                )

            raise

        # ----------------------------------------------------
        # Send OTP
        # ----------------------------------------------------

        success, message = generate_and_send_otp(
            email,
            "registration",
            name
        )

        if not success:

            flash(
                message,
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        session[
            "pending_verification_email"
        ] = email

        flash(
            "Registration submitted! "
            "Please enter the 6-digit OTP sent to your email.",
            "success"
        )

        return redirect(
            url_for("auth.verify_otp")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# OTP VERIFICATION
# ============================================================

@auth.route(
    "/verify-otp",
    methods=["GET", "POST"]
)
def verify_otp_route():

    email = (
        session.get(
            "pending_verification_email"
        )
        or
        request.args.get(
            "email",
            ""
        ).strip().lower()
    )

    if not email:

        flash(
            "No pending verification found. "
            "Please register or login.",
            "error"
        )

        return redirect(
            url_for("auth.register")
        )

    if request.method == "POST":

        entered_otp = request.form.get(
            "otp",
            ""
        ).strip()

        if not entered_otp:

            flash(
                "Please enter the 6-digit verification code.",
                "error"
            )

            return render_template(
                "auth/verify_otp.html",
                email=email
            )

        success, message = verify_otp(
            email,
            entered_otp,
            "registration"
        )

        if success:

            session.pop(
                "pending_verification_email",
                None
            )

            flash(
                "Email verified successfully! "
                "You can now log in to your account.",
                "success"
            )

            return redirect(
                url_for("auth.user_login")
            )

        flash(
            message,
            "error"
        )

        return render_template(
            "auth/verify_otp.html",
            email=email
        )

    return render_template(
        "auth/verify_otp.html",
        email=email
    )


# ============================================================
# RESEND OTP
# ============================================================

@auth.route(
    "/resend-otp",
    methods=["POST"]
)
def resend_otp():

    email = (
        request.form.get(
            "email",
            ""
        ).strip().lower()
        or
        session.get(
            "pending_verification_email"
        )
    )

    if not email:

        flash(
            "Email is required to resend verification code.",
            "error"
        )

        return redirect(
            url_for("auth.register")
        )

    user = find_user_by_email(
        email
    )

    user_name = (
        user.get("name", "User")
        if user
        else "User"
    )

    success, message = generate_and_send_otp(
        email,
        "registration",
        user_name
    )

    if success:

        session[
            "pending_verification_email"
        ] = email

        flash(
            message,
            "success"
        )

    else:

        flash(
            message,
            "error"
        )

    return redirect(
        url_for(
            "auth.verify_otp",
            email=email
        )
    )


# ============================================================
# USER LOGIN
# ============================================================

@auth.route(
    "/login",
    methods=["GET", "POST"]
)
@auth.route(
    "/user/login",
    methods=["GET", "POST"]
)
def user_login():

    next_url = (
        request.args.get("next")
        or
        request.form.get("next")
    )

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:

            flash(
                "Email and password are required.",
                "error"
            )

            return redirect(
                url_for(
                    "auth.user_login",
                    next=next_url
                )
            )

        user = find_user_by_email(
            email
        )

        if (
            user
            and check_password_hash(
                user.get("password_hash", ""),
                password
            )
        ):

            if user.get("role") != "user":

                flash(
                    "This login portal is only for standard users.",
                    "error"
                )

                return redirect(
                    url_for("auth.user_login")
                )

            # ------------------------------------------------
            # Email verification
            # ------------------------------------------------

            if not user.get(
                "is_verified",
                False
            ):

                success, message = generate_and_send_otp(
                    user["email"],
                    "registration",
                    user.get(
                        "name",
                        "User"
                    )
                )

                session[
                    "pending_verification_email"
                ] = user["email"]

                if success:

                    flash(
                        "Your account email is not yet verified. "
                        "A fresh OTP code has been sent.",
                        "error"
                    )

                else:

                    flash(
                        message,
                        "error"
                    )

                return redirect(
                    url_for("auth.verify_otp")
                )

            # ------------------------------------------------
            # Create authenticated session
            # ------------------------------------------------

            session.clear()

            session["user_id"] = user["_id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]

            flash(
                f"Welcome back, {user['name']}!",
                "success"
            )

            if (
                next_url
                and is_safe_url(next_url)
            ):
                return redirect(
                    next_url
                )

            return redirect(
                url_for("user.dashboard")
            )

        flash(
            "Invalid user email or password.",
            "error"
        )

        return redirect(
            url_for(
                "auth.user_login",
                next=next_url
            )
        )

    return render_template(
        "auth/user_login.html",
        next=next_url
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@auth.route(
    "/admin-login",
    methods=["GET", "POST"]
)
@auth.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    next_url = (
        request.args.get("next")
        or
        request.form.get("next")
    )

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:

            flash(
                "Email and password are required.",
                "error"
            )

            return redirect(
                url_for(
                    "auth.admin_login",
                    next=next_url
                )
            )

        user = find_user_by_email(
            email
        )

        if (
            user
            and check_password_hash(
                user.get("password_hash", ""),
                password
            )
        ):

            if user.get("role") != "admin":

                flash(
                    "This login portal is restricted to administrators.",
                    "error"
                )

                return redirect(
                    url_for("auth.admin_login")
                )

            session.clear()

            session["user_id"] = user["_id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]

            flash(
                "Welcome to Admin Dashboard.",
                "success"
            )

            if (
                next_url
                and is_safe_url(next_url)
            ):
                return redirect(
                    next_url
                )

            return redirect(
                url_for("admin.dashboard")
            )

        flash(
            "Invalid admin email or password.",
            "error"
        )

        return redirect(
            url_for(
                "auth.admin_login",
                next=next_url
            )
        )

    return render_template(
        "auth/admin_login.html",
        next=next_url
    )


# ============================================================
# LOGOUT
# ============================================================

@auth.route("/logout")
def logout():

    session.clear()

    flash(
        "Logged out successfully.",
        "success"
    )

    return redirect(
        url_for("news.homepage")
    )


# ============================================================
# VERIFY OTP ENDPOINT ALIAS
# ============================================================

auth.add_url_rule(
    "/verify-otp",
    endpoint="verify_otp",
    view_func=verify_otp_route,
    methods=["GET", "POST"]
)