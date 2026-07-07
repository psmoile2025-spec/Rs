from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from . import login_required

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    repo = current_app.settings_repo

    if request.method == "POST":
        raw = request.form.get("tax_rate", "").strip()
        if raw == "":
            ok = repo.set("tax_rate", "")
            if ok:
                flash("Tax rate cleared (default 8% will be used).", "success")
            else:
                flash("Could not save: the 'settings' table does not exist in the database. Please create it in Supabase: CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);", "error")
        else:
            try:
                val = float(raw)
                if val < 0 or val > 100:
                    flash("Tax rate must be between 0 and 100.", "error")
                else:
                    ok = repo.set("tax_rate", str(val))
                    if ok:
                        flash("Tax rate updated.", "success")
                    else:
                        flash("Could not save: the 'settings' table does not exist in the database. Please create it in Supabase: CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);", "error")
            except ValueError:
                flash("Invalid tax rate value.", "error")
        return redirect(url_for("settings.index"))

    current_tax_rate = repo.get("tax_rate")
    return render_template("settings.html", current_tax_rate=current_tax_rate)