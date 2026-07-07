from datetime import date, datetime
import csv
from io import StringIO

from flask import Blueprint, render_template, request, jsonify, current_app, make_response
from . import login_required

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/sales", methods=["GET"])
@login_required
def sales():
    from_date = _parse_date(request.args.get("from"), date.today())
    to_date = _parse_date(request.args.get("to"), date.today())

    summary = current_app.report_service.get_sales_summary(from_date, to_date)
    orders = current_app.report_service.get_orders_in_range(from_date, to_date)

    return render_template(
        "reports/sales.html",
        summary=summary,
        orders=orders,
        from_date=from_date,
        to_date=to_date,
    )


@reports_bp.route("/sales/export", methods=["GET"])
@login_required
def export_sales():
    from_date = _parse_date(request.args.get("from"), date.today())
    to_date = _parse_date(request.args.get("to"), date.today())

    orders = current_app.report_service.get_orders_in_range(from_date, to_date)

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["Order #", "Status", "Subtotal", "Tax", "Total", "Payment", "Created", "Paid At"])

    for o in orders:
        writer.writerow([
            o.order_number,
            o.status,
            float(o.subtotal),
            float(o.tax),
            float(o.total),
            o.payment_type or "",
            o.created_at,
            o.paid_at or "",
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Type"] = "text/csv"
    output.headers["Content-Disposition"] = f"attachment; filename=sales_{from_date}_{to_date}.csv"
    return output


@reports_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    stats = current_app.report_service.get_dashboard_stats()
    return render_template("dashboard.html", stats=stats)


def _parse_date(value: str, default: date) -> date:
    if not value:
        return default
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return default
