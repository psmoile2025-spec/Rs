from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from .order_item import OrderItem


class OrderStatus:
    OPEN = "open"
    PAID = "paid"
    CANCELLED = "cancelled"

    VALID_STATUSES = {OPEN, PAID, CANCELLED}


@dataclass
class Order:
    id: str
    order_number: str
    status: str
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    created_by: str
    payment_type: Optional[str] = None
    created_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    items: List[OrderItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        return cls(
            id=data["id"],
            order_number=data["order_number"],
            status=data["status"],
            subtotal=Decimal(str(data["subtotal"])),
            tax=Decimal(str(data["tax"])),
            total=Decimal(str(data["total"])),
            created_by=data["created_by"],
            payment_type=data.get("payment_type"),
            created_at=data.get("created_at"),
            paid_at=data.get("paid_at"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_number": self.order_number,
            "status": self.status,
            "subtotal": str(self.subtotal),
            "tax": str(self.tax),
            "total": str(self.total),
            "created_by": self.created_by,
            "payment_type": self.payment_type,
            "created_at": self.created_at,
            "paid_at": self.paid_at,
        }

    def to_summary(self) -> dict:
        return {
            "id": self.id,
            "order_number": self.order_number,
            "status": self.status,
            "subtotal": float(self.subtotal),
            "tax": float(self.tax),
            "total": float(self.total),
            "items": [
                {
                    "id": i.id,
                    "name": i.item_name or i.menu_item_id,
                    "quantity": i.quantity,
                    "unit_price": float(i.unit_price),
                    "line_total": float(i.line_total),
                }
                for i in self.items
            ],
        }
