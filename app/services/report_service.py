from typing import List, Dict, Any, Optional
from datetime import datetime, date, timezone
from decimal import Decimal
from collections import Counter

from ..interfaces import ReportServiceInterface, OrderRepository, OrderItemRepository, MenuItemRepository
from ..models import Order


class ReportService(ReportServiceInterface):
    def __init__(
        self,
        order_repo: OrderRepository,
        order_item_repo: OrderItemRepository,
        menu_item_repo: MenuItemRepository,
    ):
        self._order_repo = order_repo
        self._order_item_repo = order_item_repo
        self._menu_item_repo = menu_item_repo

    def get_sales_summary(self, from_date: date, to_date: date) -> Dict[str, Any]:
        from_dt = datetime.combine(from_date, datetime.min.time(), tzinfo=timezone.utc)
        to_dt = datetime.combine(to_date, datetime.max.time(), tzinfo=timezone.utc)

        orders = self._order_repo.get_by_date_range(from_dt, to_dt)
        paid_orders = [o for o in orders if o.status == "paid"]

        total_revenue = sum(Decimal(str(o.total)) for o in paid_orders)
        total_tax = sum(Decimal(str(o.tax)) for o in paid_orders)
        total_subtotal = sum(Decimal(str(o.subtotal)) for o in paid_orders)
        total_cost = self._calculate_total_cost(paid_orders)
        total_profit = total_subtotal - total_cost if total_cost is not None else None

        return {
            "order_count": len(paid_orders),
            "total_revenue": float(total_revenue),
            "total_tax": float(total_tax),
            "total_subtotal": float(total_subtotal),
            "total_cost": float(total_cost) if total_cost is not None else None,
            "total_profit": float(total_profit) if total_profit is not None else None,
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat(),
        }

    def get_orders_in_range(self, from_date: date, to_date: date) -> List[Order]:
        from_dt = datetime.combine(from_date, datetime.min.time(), tzinfo=timezone.utc)
        to_dt = datetime.combine(to_date, datetime.max.time(), tzinfo=timezone.utc)
        orders = self._order_repo.get_by_date_range(from_dt, to_dt)
        for order in orders:
            order.items = self._order_item_repo.list_by_order(order.id)
        return orders

    def get_dashboard_stats(self) -> Dict[str, Any]:
        today = date.today()
        summary = self.get_sales_summary(today, today)
        active_orders = self._order_repo.list_active()
        popular_items = self._get_popular_items(today)

        return {
            "open_orders": len(active_orders),
            "today_revenue": summary["total_revenue"],
            "today_order_count": summary["order_count"],
            "today_subtotal": summary["total_subtotal"],
            "today_tax": summary["total_tax"],
            "today_cost": summary["total_cost"],
            "today_profit": summary["total_profit"],
            "popular_items": popular_items,
        }

    def get_profit_loss(self, from_date: date, to_date: date) -> Dict[str, Any]:
        summary = self.get_sales_summary(from_date, to_date)
        orders = self.get_orders_in_range(from_date, to_date)
        paid_orders = [o for o in orders if o.status == "paid"]

        item_profits = self._calculate_item_profits(paid_orders)

        return {
            **summary,
            "item_breakdown": item_profits,
            "margin": (
                round((summary["total_profit"] / summary["total_subtotal"]) * 100, 2)
                if summary.get("total_subtotal") and summary["total_subtotal"] > 0
                else 0
            ),
        }

    def _get_popular_items(self, for_date: date, limit: int = 5) -> List[Dict[str, Any]]:
        from_dt = datetime.combine(for_date, datetime.min.time(), tzinfo=timezone.utc)
        to_dt = datetime.combine(for_date, datetime.max.time(), tzinfo=timezone.utc)
        orders = self._order_repo.get_by_date_range(from_dt, to_dt)
        paid_order_ids = [o.id for o in orders if o.status == "paid"]

        counts: Counter = Counter()

        for oid in paid_order_ids:
            items = self._order_item_repo.list_by_order(oid)
            for item in items:
                name = item.item_name or item.menu_item_id
                counts[name] += item.quantity

        return [{"name": name, "quantity": qty} for name, qty in counts.most_common(limit)]

    def _calculate_total_cost(self, paid_orders: List[Order]) -> Optional[Decimal]:
        cost_map = self._build_cost_map()
        if cost_map is None:
            return None

        total = Decimal("0")
        for order in paid_orders:
            items = self._order_item_repo.list_by_order(order.id)
            for item in items:
                unit_cost = cost_map.get(item.menu_item_id)
                if unit_cost is not None:
                    total += unit_cost * Decimal(str(item.quantity))
        return total

    def _calculate_item_profits(self, paid_orders: List[Order]) -> List[Dict[str, Any]]:
        cost_map = self._build_cost_map()
        if cost_map is None:
            return []

        item_data: Dict[str, Dict] = {}
        for order in paid_orders:
            items = self._order_item_repo.list_by_order(order.id)
            for item in items:
                name = item.item_name or item.menu_item_id
                if name not in item_data:
                    item_data[name] = {
                        "name": name,
                        "quantity": 0,
                        "revenue": Decimal("0"),
                        "cost": Decimal("0"),
                    }
                unit_cost = cost_map.get(item.menu_item_id, Decimal("0"))
                item_data[name]["quantity"] += item.quantity
                item_data[name]["revenue"] += Decimal(str(item.line_total))
                item_data[name]["cost"] += unit_cost * Decimal(str(item.quantity))

        result = []
        for data in item_data.values():
            profit = data["revenue"] - data["cost"]
            result.append({
                "name": data["name"],
                "quantity": data["quantity"],
                "revenue": float(data["revenue"]),
                "cost": float(data["cost"]),
                "profit": float(profit),
            })
        return sorted(result, key=lambda x: x["profit"], reverse=True)

    def _build_cost_map(self) -> Optional[Dict[str, Decimal]]:
        items = self._menu_item_repo.list()
        cost_map: Dict[str, Decimal] = {}
        any_have_cost = False
        for item in items:
            if item.cost is not None:
                cost_map[item.id] = item.cost
                any_have_cost = True
            else:
                cost_map[item.id] = Decimal("0")
        if not any_have_cost:
            return None
        return cost_map
