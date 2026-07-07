from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date
from decimal import Decimal

from ..models import Order


class ReportServiceInterface(ABC):
    @abstractmethod
    def get_sales_summary(self, from_date: date, to_date: date) -> Dict[str, Any]:
        ...

    @abstractmethod
    def get_orders_in_range(self, from_date: date, to_date: date) -> List[Order]:
        ...

    @abstractmethod
    def get_dashboard_stats(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def get_profit_loss(self, from_date: date, to_date: date) -> Dict[str, Any]:
        ...
