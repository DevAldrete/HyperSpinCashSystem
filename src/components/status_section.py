from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import flet as ft
from controllers.analytics import AnalyticsService
from utils.logger import get_logger
from utils.theme import AppColors, AppTextStyles, AppSpacing


logger = get_logger()

class StatusSection(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = AppSpacing.MEDIUM
        self.analytics = AnalyticsService()

        self.inventory_value_text = self._metric_value_text()
        self.revenue_value_text = self._metric_value_text()
        self.profit_value_text = self._metric_value_text()
        self.margin_value_text = self._metric_value_text()
        self.low_stock_value_text = self._metric_value_text()

        self.stock_pie_chart = ft.PieChart(
            sections=[],
            sections_space=0,
            center_space_radius=40,
            expand=True,
        )
        self.payment_pie_chart = ft.PieChart(
            sections=[],
            sections_space=0,
            center_space_radius=40,
            expand=True,
        )
        self.revenue_bar_chart = ft.BarChart(
            bar_groups=[],
            border=ft.border.all(1, AppColors.BORDER),
            left_axis=ft.ChartAxis(labels_size=40),
            bottom_axis=ft.ChartAxis(labels_size=40),
            horizontal_grid_lines=ft.ChartGridLines(
                color=AppColors.GRID_LINES,
                width=1,
                dash_pattern=[3, 3],
            ),
            tooltip_bgcolor=AppColors.TOOLTIP_BG,
            expand=True,
        )

        metrics_row = ft.Row(
            [
                self.create_metric_card("Inventory Value", self.inventory_value_text, ft.Icons.INVENTORY),
                self.create_metric_card("Revenue", self.revenue_value_text, ft.Icons.ATTACH_MONEY),
                self.create_metric_card("Profit", self.profit_value_text, ft.Icons.MONEY),
                self.create_metric_card("Margin", self.margin_value_text, ft.Icons.PERCENT),
                self.create_metric_card("Low Stock", self.low_stock_value_text, ft.Icons.WARNING),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        charts_row = ft.Row(
            [
                ft.Container(
                    content=ft.Column([
                        ft.Text("Stock Distribution (Top 5)", style=AppTextStyles.HEADER_SMALL),
                        self.stock_pie_chart,
                    ]),
                    expand=True,
                    height=300,
                    padding=AppSpacing.SMALL,
                    border=ft.border.all(1, AppColors.BORDER),
                    border_radius=10,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Payment Methods", style=AppTextStyles.HEADER_SMALL),
                        self.payment_pie_chart,
                    ]),
                    expand=True,
                    height=300,
                    padding=AppSpacing.SMALL,
                    border=ft.border.all(1, AppColors.BORDER),
                    border_radius=10,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Sales Trend", style=AppTextStyles.HEADER_SMALL),
                        self.revenue_bar_chart,
                    ]),
                    expand=True,
                    height=300,
                    padding=AppSpacing.SMALL,
                    border=ft.border.all(1, AppColors.BORDER),
                    border_radius=10,
                ),
            ],
            expand=True,
        )

        self.period_dropdown = ft.Dropdown(
            width=200,
            options=[
                ft.dropdown.Option("today", "Today"),
                ft.dropdown.Option("week", "Last 7 Days"),
                ft.dropdown.Option("month", "This Month"),
                ft.dropdown.Option("all", "All Time"),
            ],
            value="week",
            on_change=self.on_period_change,
        )

        self.loading_indicator = ft.ProgressBar(visible=False, color=AppColors.PRIMARY)

        header = ft.Row(
            [
                ft.Text("General Status", style=AppTextStyles.HEADER_LARGE),
                self.period_dropdown,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.content = ft.Column(
            [
                self.loading_indicator,
                header,
                ft.Divider(color=AppColors.DIVIDER),
                metrics_row,
                ft.Divider(color=AppColors.DIVIDER),
                charts_row,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        self.load_data()

    def on_period_change(self, e):
        self.load_data()

    def _metric_value_text(self) -> ft.Text:
        return ft.Text("—", style=AppTextStyles.METRIC_VALUE)

    def create_metric_card(self, title: str, value_control: ft.Text, icon) -> ft.Card:
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(icon, size=40, color=AppColors.PRIMARY),
                        ft.Text(title, style=AppTextStyles.LABEL_BOLD),
                        value_control,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=AppSpacing.MEDIUM,
                width=250,
                height=150,
            )
        )

    def load_data(self):
        self.loading_indicator.visible = True
        if self.page:
            self.update()

        period = self.period_dropdown.value
        start_date: Optional[datetime] = None
        end_date: Optional[datetime] = datetime.utcnow()
        
        if period == "today":
            start_date = datetime(end_date.year, end_date.month, end_date.day)
        elif period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = datetime(end_date.year, end_date.month, 1)
        elif period == "all":
            start_date = None
            end_date = None

        try:
            snapshot = self.analytics.get_dashboard_snapshot(
                start_date=start_date,
                end_date=end_date
            )
        except Exception as exc:
            logger.exception("Failed to load dashboard data: %s", exc)
            if self.page:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Unable to load dashboard data."),
                        bgcolor=AppColors.ERROR,
                    )
                )
            self.loading_indicator.visible = False
            if self.page:
                self.update()
            return

        self.inventory_value_text.value = f"${snapshot.inventory_value:,.2f}"
        self.revenue_value_text.value = f"${snapshot.total_revenue:,.2f}"
        self.profit_value_text.value = f"${snapshot.total_profit:,.2f}"
        
        if snapshot.total_revenue > 0:
            margin = (snapshot.total_profit / snapshot.total_revenue) * 100
            self.margin_value_text.value = f"{margin:.1f}%"
        else:
            self.margin_value_text.value = "0.0%"

        self.low_stock_value_text.value = str(snapshot.low_stock_count)

        self._update_stock_chart(snapshot.stock_distribution)
        self._update_sales_chart(snapshot.sales_trends)
        self._update_payment_chart(snapshot.payment_method_distribution)

        self.loading_indicator.visible = False
        if self.page:
            self.update()

    def _update_payment_chart(self, distribution: List[Dict[str, Any]]):
        colors = [
            AppColors.CHART_1,
            AppColors.CHART_2,
            AppColors.CHART_3,
            AppColors.CHART_4,
            AppColors.CHART_5,
        ]

        if not distribution:
            self.payment_pie_chart.sections = []
            return

        sections = []
        for index, item in enumerate(distribution):
            sections.append(
                ft.PieChartSection(
                    value=item["total"],
                    title=f"${item['total']:.0f}",
                    color=colors[index % len(colors)],
                    radius=100,
                    title_style=AppTextStyles.CHART_LABEL,
                    badge=ft.Text(item["method"].replace("_", " ").title(), size=10),
                )
            )

        self.payment_pie_chart.sections = sections

    def _update_stock_chart(self, distribution: List[Dict[str, Any]]):
        colors = [
            AppColors.CHART_1,
            AppColors.CHART_2,
            AppColors.CHART_3,
            AppColors.CHART_4,
            AppColors.CHART_5,
        ]

        if not distribution:
            self.stock_pie_chart.sections = []
            return

        sections = []
        for index, item in enumerate(distribution):
            sections.append(
                ft.PieChartSection(
                    value=item["quantity"],
                    title=str(item["quantity"]),
                    color=colors[index % len(colors)],
                    radius=100,
                    title_style=AppTextStyles.CHART_LABEL,
                    badge=ft.Text(item["name"], size=10),
                )
            )

        self.stock_pie_chart.sections = sections

    def _update_sales_chart(self, trends: List[Dict[str, Any]]):
        if not trends:
            self.revenue_bar_chart.bar_groups = []
            self.revenue_bar_chart.bottom_axis.labels = []
            self.revenue_bar_chart.max_y = 0
            return

        bar_groups = []
        axis_labels = []
        max_amount = 0.0

        for index, entry in enumerate(trends):
            amount = entry["revenue"]
            max_amount = max(max_amount, amount)
            bar_groups.append(
                ft.BarChartGroup(
                    x=index,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=amount,
                            width=30,
                            color=AppColors.CHART_BAR,
                            tooltip=f"${amount:.2f}\n{entry['label']}",
                            border_radius=5,
                        )
                    ],
                )
            )
            axis_labels.append(
                ft.ChartAxisLabel(
                    value=index,
                    label=ft.Text(entry["label"], size=10),
                )
            )

        self.revenue_bar_chart.bar_groups = bar_groups
        self.revenue_bar_chart.bottom_axis.labels = axis_labels
        self.revenue_bar_chart.max_y = max_amount * 1.2 if max_amount else 1
