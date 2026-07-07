from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Category:
    id: str
    name: str
    sort_order: int = 0
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        return cls(
            id=data["id"],
            name=data["name"],
            sort_order=data.get("sort_order", 0),
            created_at=data.get("created_at"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "sort_order": self.sort_order,
            "created_at": self.created_at,
        }
