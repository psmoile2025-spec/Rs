from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class OrderItem:
    id: str
    order_id: str
    menu_item_id: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    item_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "OrderItem":
        return cls(
            id=data["id"],
            order_id=data["order_id"],
            menu_item_id=data["menu_item_id"],
            quantity=data["quantity"],
            unit_price=Decimal(str(data["unit_price"])),
            line_total=Decimal(str(data["line_total"])),
            item_name=data.get("item_name"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "menu_item_id": self.menu_item_id,
            "quantity": self.quantity,
            "unit_price": str(self.unit_price),
            "line_total": str(self.line_total),
            "item_name": self.item_name,
        }
