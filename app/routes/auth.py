from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = current_app.auth_service.login(email, password)
        if user:
            session["user_id"] = user.id
            session["user_name"] = user.display_name
            flash("Logged in successfully.", "success")
            return redirect(url_for("pos.pos_index"))
        flash("Invalid email or password.", "error")
        return render_template("login.html")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    user = current_app.auth_service.get_current_user(session["user_id"])
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("auth.logout"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "profile":
            display_name = request.form.get("display_name", "").strip()
            email = request.form.get("email", "").strip()
            if display_name and email:
                current_app.user_repo.update(user.id, display_name=display_name, email=email)
                session["user_name"] = display_name
                flash("Profile updated.", "success")
            else:
                flash("Name and email are required.", "error")

        elif action == "password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not check_password_hash(user.password_hash, current_password):
                flash("Current password is incorrect.", "error")
            elif len(new_password) < 6:
                flash("New password must be at least 6 characters.", "error")
            elif new_password != confirm_password:
                flash("New passwords do not match.", "error")
            else:
                hashed = generate_password_hash(new_password)
                current_app.user_repo.update(user.id, password_hash=hashed)
                flash("Password changed.", "success")

        return redirect(url_for("auth.account"))

    return render_template("account.html", user=user)
