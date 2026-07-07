from dataclasses import dataclass
from typing import Optional


@dataclass
class Setting:
    key: str
    value: str

    @classmethod
    def from_dict(cls, data: dict) -> "Setting":
        return cls(key=data["key"], value=data.get("value", ""))

    def to_dict(self) -> dict:
        return {"key": self.key, "value": self.value}