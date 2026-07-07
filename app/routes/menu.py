from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from . import login_required

menu_bp = Blueprint("menu", __name__, url_prefix="/menu")


@menu_bp.route("/categories", methods=["GET"])
@login_required
def list_categories():
    categories = current_app.menu_service.list_categories()
    return render_template("menu/categories.html", categories=categories)


@menu_bp.route("/categories", methods=["POST"])
@login_required
def create_category():
    name = request.form.get("name", "").strip()
    sort_order = int(request.form.get("sort_order", 0))
    if not name:
        flash("Category name is required.", "error")
        return redirect(url_for("menu.list_categories"))
    current_app.menu_service.create_category(name, sort_order)
    flash("Category created.", "success")
    return redirect(url_for("menu.list_categories"))


@menu_bp.route("/categories/<id>/edit", methods=["POST"])
@login_required
def update_category(id):
    name = request.form.get("name", "").strip()
    sort_order = request.form.get("sort_order", type=int)
    current_app.menu_service.update_category(id, name=name if name else None, sort_order=sort_order)
    flash("Category updated.", "success")
    return redirect(url_for("menu.list_categories"))


@menu_bp.route("/categories/<id>/delete", methods=["POST"])
@login_required
def delete_category(id):
    current_app.menu_service.delete_category(id)
    flash("Category deleted.", "success")
    return redirect(url_for("menu.list_categories"))


@menu_bp.route("/items", methods=["GET"])
@login_required
def list_items():
    category_id = request.args.get("category_id")
    items = current_app.menu_service.list_items(category_id)
    categories = current_app.menu_service.list_categories()
    return render_template("menu/items.html", items=items, categories=categories)


@menu_bp.route("/items", methods=["POST"])
@login_required
def create_item():
    category_id = request.form.get("category_id", "").strip()
    name = request.form.get("name", "").strip()
    price = float(request.form.get("price", 0))
    description = request.form.get("description", "").strip() or None
    cost_raw = request.form.get("cost", "").strip()
    cost = float(cost_raw) if cost_raw else None
    image_url = request.form.get("image_url", "").strip() or None

    if not name or not category_id or price <= 0:
        flash("Name, category, and valid price are required.", "error")
        return redirect(url_for("menu.list_items"))

    current_app.menu_service.create_item(category_id, name, price, description, cost, image_url)
    flash("Menu item created.", "success")
    return redirect(url_for("menu.list_items"))


@menu_bp.route("/items/<id>/edit", methods=["POST"])
@login_required
def update_item(id):
    updates = {}
    for field in ("name", "description", "category_id"):
        val = request.form.get(field)
        if val is not None and val.strip():
            updates[field] = val.strip()
    price = request.form.get("price", type=float)
    if price is not None and price > 0:
        updates["price"] = price
    cost_raw = request.form.get("cost", "").strip()
    if cost_raw:
        updates["cost"] = float(cost_raw)
    image_url = request.form.get("image_url", "").strip()
    updates["image_url"] = image_url if image_url else None

    if updates:
        current_app.menu_service.update_item(id, **updates)
    flash("Menu item updated.", "success")
    return redirect(url_for("menu.list_items"))


@menu_bp.route("/items/<id>/toggle", methods=["POST"])
@login_required
def toggle_item(id):
    current_app.menu_service.toggle_item_available(id)
    flash("Item availability toggled.", "success")
    return redirect(url_for("menu.list_items"))


@menu_bp.route("/items/<id>/delete", methods=["POST"])
@login_required
def delete_item(id):
    current_app.menu_service.delete_item(id)
    flash("Menu item deleted.", "success")
    return redirect(url_for("menu.list_items"))
