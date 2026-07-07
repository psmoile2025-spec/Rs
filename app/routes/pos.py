from flask import Blueprint, render_template, request, jsonify, session, current_app, flash, redirect, url_for
from ..services.pos_service import OrderError
from . import login_required

pos_bp = Blueprint("pos", __name__)


@pos_bp.route("/")
@login_required
def pos_index():
    categories, items = current_app.pos_service.get_menu_data()
    active_orders = current_app.pos_service.list_active_orders()
    return render_template(
        "pos/index.html",
        categories=categories,
        items=items,
        active_orders=active_orders,
    )


@pos_bp.route("/pos/orders", methods=["GET"])
@login_required
def list_orders():
    orders = current_app.pos_service.list_active_orders()
    return render_template("pos/order_list.html", orders=orders)


@pos_bp.route("/pos/orders", methods=["POST"])
@login_required
def create_order():
    order = current_app.pos_service.create_order(session["user_id"])
    return jsonify({"id": order.id, "order_number": order.order_number})


@pos_bp.route("/pos/orders/<order_id>")
@login_required
def view_order(order_id):
    order = current_app.pos_service.get_order_with_items(order_id)
    if not order:
        return "Order not found", 404
    return render_template("pos/order_detail.html", order=order)


@pos_bp.route("/pos/orders/active/json")
@login_required
def active_orders_json():
    orders = current_app.pos_service.list_active_orders()
    return jsonify({
        "success": True,
        "orders": [
            {"id": o.id, "order_number": o.order_number, "total": float(o.total)}
            for o in orders
        ],
    })


@pos_bp.route("/pos/orders/<order_id>/json")
@login_required
def view_order_json(order_id):
    order = current_app.pos_service.get_order_with_items(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify({"success": True, "order": order.to_summary()})


@pos_bp.route("/pos/orders/<order_id>/items", methods=["POST"])
@login_required
def add_item(order_id):
    data = request.get_json()
    menu_item_id = data.get("menu_item_id")
    quantity = int(data.get("quantity", 1))

    try:
        item = current_app.pos_service.add_item_to_order(order_id, menu_item_id, quantity)
        order = current_app.pos_service.get_order_with_items(order_id)
        return jsonify({
            "success": True,
            "item": item.to_dict(),
            "order": order.to_summary(),
        })
    except (OrderError, ValueError) as e:
        return jsonify({"success": False, "error": str(e)}), 400


@pos_bp.route("/pos/orders/<order_id>/items/<item_id>", methods=["DELETE"])
@login_required
def remove_item(order_id, item_id):
    try:
        success = current_app.pos_service.remove_item_from_order(order_id, item_id)
        if not success:
            return jsonify({"success": False}), 404
        order = current_app.pos_service.get_order_with_items(order_id)
        return jsonify({"success": True, "order": order.to_summary()})
    except OrderError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@pos_bp.route("/pos/orders/<order_id>/pay", methods=["POST"])
@login_required
def pay_order(order_id):
    data = request.get_json()
    payment_type = data.get("payment_type", "cash")

    try:
        order = current_app.pos_service.pay_order(order_id, payment_type)
        return jsonify({"success": True, "order": order.to_summary()})
    except OrderError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@pos_bp.route("/pos/orders/<order_id>/cancel", methods=["POST"])
@login_required
def cancel_order(order_id):
    is_ajax = request.content_type == "application/json"
    try:
        order = current_app.pos_service.cancel_order(order_id)
        if not order:
            if is_ajax:
                return jsonify({"success": False, "error": "Order not found"}), 404
            flash("Order not found.", "error")
        else:
            if is_ajax:
                return jsonify({"success": True, "order": order.to_summary()})
            flash(f"Order {order.order_number} cancelled.", "success")
    except OrderError as e:
        if is_ajax:
            return jsonify({"success": False, "error": str(e)}), 400
        flash(str(e), "error")
    return redirect(request.referrer or url_for("pos.pos_index"))
