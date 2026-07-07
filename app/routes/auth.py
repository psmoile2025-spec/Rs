from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
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


@auth_bp.route("/users", methods=["GET", "POST"])
@login_required
def manage_users():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        display_name = request.form.get("display_name", "").strip()

        if not email or not password or not display_name:
            flash("All fields are required.", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
        else:
            try:
                current_app.auth_service.create_user(email, password, display_name)
                flash(f"User '{display_name}' created.", "success")
            except ValueError as e:
                flash(str(e), "error")

        return redirect(url_for("auth.manage_users"))

    users = current_app.auth_service.list_users()
    return render_template("users.html", users=users)


@auth_bp.route("/users/<user_id>/edit", methods=["POST"])
@login_required
def edit_user(user_id):
    email = request.form.get("email", "").strip()
    display_name = request.form.get("display_name", "").strip()
    password = request.form.get("password", "")

    if not email or not display_name:
        return jsonify({"success": False, "error": "Name and email are required."}), 400

    user = current_app.auth_service.update_user(user_id, email, display_name)
    if not user:
        return jsonify({"success": False, "error": "User not found."}), 404

    if password:
        if len(password) < 6:
            return jsonify({"success": False, "error": "Password must be at least 6 characters."}), 400
        hashed = generate_password_hash(password)
        current_app.user_repo.update(user_id, password_hash=hashed)

    return jsonify({"success": True, "user": user.to_dict()})


@auth_bp.route("/users/<user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    if user_id == session.get("user_id"):
        return jsonify({"success": False, "error": "You cannot delete your own account."}), 400

    deleted = current_app.auth_service.delete_user(user_id)
    if not deleted:
        return jsonify({"success": False, "error": "User not found."}), 404

    return jsonify({"success": True})
