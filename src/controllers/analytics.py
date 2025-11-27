from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Generator, List, Optional

from sqlalchemy import func
from sqlmodel import Session, select

from db.conn import engine
from models.item import Product
from models.sale import Sale, SaleItem
from models.payment import Payment, PaymentStatus


class AnalyticsGranularity(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@dataclass(slots=True)
class DashboardSnapshot:
    inventory_value: float
    total_revenue: float
    total_profit: float
    low_stock_count: int
    stock_distribution: List[Dict[str, Any]]
    recent_sales: List[Sale]
    sales_trends: List[Dict[str, Any]]
    payment_method_distribution: List[Dict[str, Any]]


class AnalyticsService:
    """Central place for expensive dashboard/analytics queries."""

    def __init__(self, session: Optional[Session] = None):
        self._session = session

    @contextmanager
    def _session_scope(self) -> Generator[Session, None, None]:
        if self._session:
            yield self._session
            return

        with Session(engine) as session:
            yield session

    # Public API -----------------------------------------------------------------

    def get_inventory_metrics(self, *, low_stock_threshold: int = 5) -> Dict[str, Any]:
        with self._session_scope() as session:
            return self._inventory_metrics(session, low_stock_threshold)

    def get_revenue_metrics(
        self,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        with self._session_scope() as session:
            return self._revenue_metrics(session, start, end)

    def get_stock_distribution(self, *, top_n: int = 5) -> List[Dict[str, Any]]:
        with self._session_scope() as session:
            return self._stock_distribution(session, top_n)

    def get_category_distribution(self) -> List[Dict[str, Any]]:
        with self._session_scope() as session:
            return self._category_distribution(session)

    def get_recent_sales(self, *, limit: int = 5) -> List[Sale]:
        with self._session_scope() as session:
            return self._recent_sales(session, limit)

    def get_sales_aggregations(
        self,
        *,
        granularity: AnalyticsGranularity = AnalyticsGranularity.DAY,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        with self._session_scope() as session:
            return self._sales_trends(session, granularity, start, end)

    def get_dashboard_snapshot(
        self,
        *,
        low_stock_threshold: int = 5,
        top_n_products: int = 5,
        sales_limit: int = 5,
        granularity: AnalyticsGranularity = AnalyticsGranularity.DAY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> DashboardSnapshot:
        with self._session_scope() as session:
            inventory = self._inventory_metrics(session, low_stock_threshold)
            revenue = self._revenue_metrics(session, start_date, end_date)
            stock_distribution = self._stock_distribution(session, top_n_products)
            recent_sales = self._recent_sales(session, sales_limit)
            sales_trends = self._sales_trends(session, granularity, start_date, end_date)
            payment_distribution = self._payment_method_distribution(session, start_date, end_date)

        return DashboardSnapshot(
            inventory_value=inventory["inventory_value"],
            total_revenue=revenue["total_revenue"],
            total_profit=revenue["total_profit"],
            low_stock_count=inventory["low_stock_count"],
            stock_distribution=stock_distribution,
            recent_sales=recent_sales,
            sales_trends=sales_trends,
            payment_method_distribution=payment_distribution,
        )

    # Internal helpers -----------------------------------------------------------

    def _inventory_metrics(self, session: Session, low_stock_threshold: int) -> Dict[str, Any]:
        value_statement = select(
            func.coalesce(func.sum(Product.price * Product.quantity), 0.0)
        )
        total_inventory_value = session.exec(value_statement).one()

        low_stock_statement = select(func.count(Product.id)).where(
            Product.quantity < low_stock_threshold
        )
        low_stock_count = session.exec(low_stock_statement).one()

        return {
            "inventory_value": float(total_inventory_value or 0.0),
            "low_stock_count": int(low_stock_count or 0),
        }

    def _revenue_metrics(
        self,
        session: Session,
        start: Optional[datetime],
        end: Optional[datetime],
    ) -> Dict[str, Any]:
        revenue_statement = select(func.coalesce(func.sum(Sale.total_amount), 0.0)).where(
            Sale.status == "completed"
        )
        revenue_statement = self._apply_sale_window(revenue_statement, start, end)
        total_revenue = session.exec(revenue_statement).one()

        profit_value = self._profit_value(session, start, end)

        return {
            "total_revenue": float(total_revenue or 0.0),
            "total_profit": profit_value,
        }

    def _profit_value(
        self,
        session: Session,
        start: Optional[datetime],
        end: Optional[datetime],
    ) -> float:
        profit_statement = (
            select(
                func.coalesce(
                    func.sum(
                        (SaleItem.unit_price - SaleItem.cost_price)
                        * SaleItem.quantity
                    ),
                    0.0,
                )
            )
            .join(Sale, Sale.id == SaleItem.sale_id)
            .where(Sale.status == "completed")
        )
        profit_statement = self._apply_sale_window(profit_statement, start, end)
        profit = session.exec(profit_statement).one()
        return float(profit or 0.0)

    def _stock_distribution(self, session: Session, top_n: int) -> List[Dict[str, Any]]:
        statement = (
            select(Product.name, Product.quantity)
            .where(Product.quantity > 0)
            .order_by(Product.quantity.desc())
            .limit(top_n)
        )
        rows = session.exec(statement).all()
        return [
            {"name": row[0], "quantity": int(row[1])}
            for row in rows
        ]

    def _category_distribution(self, session: Session) -> List[Dict[str, Any]]:
        statement = (
            select(Product.category, func.count(Product.id))
            .group_by(Product.category)
        )
        rows = session.exec(statement).all()
        return [
            {"category": row[0] or "Uncategorized", "count": int(row[1])}
            for row in rows
        ]

    def _recent_sales(self, session: Session, limit: int) -> List[Sale]:
        statement = (
            select(Sale)
            .where(Sale.status == "completed")
            .order_by(Sale.created_at.desc())
            .limit(limit)
        )
        return session.exec(statement).all()

    def _sales_trends(
        self,
        session: Session,
        granularity: AnalyticsGranularity,
        start: Optional[datetime],
        end: Optional[datetime],
    ) -> List[Dict[str, Any]]:
        fmt = {
            AnalyticsGranularity.DAY: "%Y-%m-%d",
            AnalyticsGranularity.WEEK: "%Y-%W",
            AnalyticsGranularity.MONTH: "%Y-%m",
        }[granularity]

        if not end:
            end = datetime.utcnow()
        if not start:
            start = end - timedelta(days=30)

        statement = (
            select(
                func.strftime(fmt, Sale.created_at).label("period"),
                func.coalesce(func.sum(Sale.total_amount), 0.0).label("revenue"),
                func.count(Sale.id).label("sales"),
            )
            .where(Sale.status == "completed")
        )
        statement = self._apply_sale_window(statement, start, end)
        statement = statement.group_by("period").order_by("period")

        rows = session.exec(statement).all()
        trend = []
        for row in rows:
            period = row.period
            trend.append(
                {
                    "period": period,
                    "label": period,
                    "revenue": float(row.revenue or 0.0),
                    "sales": int(row.sales or 0),
                }
            )
        return trend

    def _payment_method_distribution(
        self,
        session: Session,
        start: Optional[datetime],
        end: Optional[datetime],
    ) -> List[Dict[str, Any]]:
        statement = (
            select(Payment.payment_method, func.count(Payment.id), func.sum(Payment.amount))
            .where(Payment.status == PaymentStatus.COMPLETED)
            .group_by(Payment.payment_method)
        )
        
        if start:
            statement = statement.where(Payment.created_at >= start)
        if end:
            statement = statement.where(Payment.created_at <= end)
            
        rows = session.exec(statement).all()
        return [
            {
                "method": row[0],
                "count": int(row[1]),
                "total": float(row[2] or 0.0)
            }
            for row in rows
        ]

    @staticmethod
    def _apply_sale_window(statement, start: Optional[datetime], end: Optional[datetime]):
        if start:
            statement = statement.where(Sale.created_at >= start)
        if end:
            statement = statement.where(Sale.created_at <= end)
        return statement
