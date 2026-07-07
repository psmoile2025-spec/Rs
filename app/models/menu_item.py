from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal


@dataclass
class MenuItem:
    id: str
    category_id: str
    name: str
    price: Decimal
    cost: Optional[Decimal] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    available: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    category_name: Optional[str] = None
    profit: Optional[Decimal] = None

    @classmethod
    def from_dict(cls, data: dict) -> "MenuItem":
        cost_raw = data.get("cost")
        cost = Decimal(str(cost_raw)) if cost_raw is not None else None
        price = Decimal(str(data["price"]))
        profit = (price - cost) if cost is not None else None
        return cls(
            id=data["id"],
            category_id=data["category_id"],
            name=data["name"],
            price=price,
            cost=cost,
            description=data.get("description"),
            image_url=data.get("image_url"),
            available=data.get("available", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            category_name=data.get("category_name"),
            profit=profit,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category_id": self.category_id,
            "name": self.name,
            "price": str(self.price),
            "cost": str(self.cost) if self.cost is not None else None,
            "description": self.description,
            "image_url": self.image_url,
            "available": self.available,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "category_name": self.category_name,
            "profit": str(self.profit) if self.profit is not None else None,
        }
