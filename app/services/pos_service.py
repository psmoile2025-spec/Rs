from typing import List, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP

from ..interfaces import POSServiceInterface, OrderRepository, OrderItemRepository, MenuItemRepository, CategoryRepository
from ..models import Order, OrderItem, MenuItem, Category, OrderStatus


class OrderError(Exception):
    pass


class POSService(POSServiceInterface):
    def __init__(
        self,
        order_repo: OrderRepository,
        order_item_repo: OrderItemRepository,
        menu_item_repo: MenuItemRepository,
        category_repo: CategoryRepository,
        tax_rate: float = 0.08,
    ):
        self._order_repo = order_repo
        self._order_item_repo = order_item_repo
        self._menu_item_repo = menu_item_repo
        self._category_repo = category_repo
        self._tax_rate = Decimal(str(tax_rate))

    def get_menu_data(self) -> Tuple[List[Category], List[MenuItem]]:
        categories = self._category_repo.list()
        items = self._menu_item_repo.list(available=True)
        return categories, items

    def create_order(self, user_id: str) -> Order:
        order_number = self._order_repo.get_next_order_number()
        return self._order_repo.create(order_number, user_id)

    def get_order(self, order_id: str) -> Optional[Order]:
        return self._order_repo.get_by_id(order_id)

    def add_item_to_order(self, order_id: str, menu_item_id: str, quantity: int = 1) -> OrderItem:
        order = self._order_repo.get_by_id(order_id)
        if not order:
            raise OrderError("Order not found")
        if order.status != OrderStatus.OPEN:
            raise OrderError(f"Cannot add items to an order with status '{order.status}'")

        menu_item = self._menu_item_repo.get_by_id(menu_item_id)
        if not menu_item:
            raise OrderError(f"Menu item {menu_item_id} not found")
        if not menu_item.available:
            raise OrderError(f"Menu item '{menu_item.name}' is not available")

        unit_price = menu_item.price
        existing = self._order_item_repo.find_by_order_and_menu_item(order_id, menu_item_id)

        if existing:
            new_qty = existing.quantity + quantity
            line_total = (unit_price * Decimal(str(new_qty))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            order_item = self._order_item_repo.update_quantity(
                id=existing.id,
                quantity=new_qty,
                line_total=float(line_total),
            )
        else:
            line_total = (unit_price * Decimal(str(quantity))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            order_item = self._order_item_repo.create(
                order_id=order_id,
                menu_item_id=menu_item_id,
                quantity=quantity,
                unit_price=float(unit_price),
                line_total=float(line_total),
            )

        self._recalculate_order(order_id)
        return order_item

    def remove_item_from_order(self, order_id: str, item_id: str) -> bool:
        order = self._order_repo.get_by_id(order_id)
        if not order:
            raise OrderError("Order not found")
        if order.status != OrderStatus.OPEN:
            raise OrderError(f"Cannot remove items from an order with status '{order.status}'")

        result = self._order_item_repo.delete(item_id)
        if result:
            self._recalculate_order(order_id)
        return result

    def pay_order(self, order_id: str, payment_type: str) -> Optional[Order]:
        order = self._order_repo.get_by_id(order_id)
        if not order:
            raise OrderError("Order not found")
        if order.status != OrderStatus.OPEN:
            raise OrderError(f"Cannot pay an order with status '{order.status}'")

        subtotal = self._calculate_subtotal(order_id)
        tax = (subtotal * self._tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total = (subtotal + tax).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return self._order_repo.mark_paid(
            id=order_id,
            payment_type=payment_type,
            total=float(total),
            tax=float(tax),
            subtotal=float(subtotal),
        )

    def cancel_order(self, order_id: str) -> Optional[Order]:
        order = self._order_repo.get_by_id(order_id)
        if not order:
            raise OrderError("Order not found")
        if order.status == OrderStatus.PAID:
            raise OrderError("Cannot cancel a paid order")
        if order.status == OrderStatus.CANCELLED:
            raise OrderError("Order is already cancelled")
        return self._order_repo.update_status(order_id, OrderStatus.CANCELLED)

    def list_active_orders(self) -> List[Order]:
        return self._order_repo.list_active()

    def get_order_with_items(self, order_id: str) -> Optional[Order]:
        order = self._order_repo.get_by_id(order_id)
        if not order:
            return None
        order.items = self._order_item_repo.list_by_order(order_id)
        return order

    def _calculate_subtotal(self, order_id: str) -> Decimal:
        items = self._order_item_repo.list_by_order(order_id)
        return Decimal(sum(Decimal(str(item.line_total)) for item in items)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def _recalculate_order(self, order_id: str) -> None:
        subtotal = self._calculate_subtotal(order_id)
        tax = (subtotal * self._tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total = (subtotal + tax).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        self._order_repo.update_totals(
            id=order_id,
            subtotal=float(subtotal),
            tax=float(tax),
            total=float(total),
        )
