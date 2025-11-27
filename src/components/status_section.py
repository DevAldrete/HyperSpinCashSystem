import flet as ft
from controllers.inventory import list_products
from controllers.payment import PaymentController
from models.payment import PaymentStatus

class StatusSection(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 20
        self.payment_controller = PaymentController()
        
        self.content = ft.Column(
            [
                ft.Text("General Status", size=30, weight="bold"),
                ft.Divider(),
                ft.Row(
                    [
                        self.create_metric_card("Total Inventory Value", "$0.00", ft.Icons.INVENTORY),
                        self.create_metric_card("Total Revenue", "$0.00", ft.Icons.ATTACH_MONEY),
                        self.create_metric_card("Low Stock Items", "0", ft.Icons.WARNING),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Stock Distribution (Top 5)", size=20, weight="bold"),
                                ft.PieChart(
                                    sections=[],
                                    sections_space=0,
                                    center_space_radius=40,
                                    expand=True,
                                )
                            ]),
                            expand=True,
                            height=300,
                            padding=10,
                            border=ft.border.all(1, ft.Colors.GREY_400),
                            border_radius=10,
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Recent Payments", size=20, weight="bold"),
                                ft.BarChart(
                                    bar_groups=[],
                                    border=ft.border.all(1, ft.Colors.GREY_400),
                                    left_axis=ft.ChartAxis(labels_size=40),
                                    bottom_axis=ft.ChartAxis(labels_size=40),
                                    horizontal_grid_lines=ft.ChartGridLines(
                                        color=ft.Colors.GREY_300,
                                        width=1,
                                        dash_pattern=[3, 3],
                                    ),
                                    tooltip_bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.GREY_300),
                                    expand=True,
                                )
                            ]),
                            expand=True,
                            height=300,
                            padding=10,
                            border=ft.border.all(1, ft.Colors.GREY_400),
                            border_radius=10,
                        ),
                    ],
                    expand=True,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        self.load_data()

    def create_metric_card(self, title, value, icon):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(icon, size=40, color=ft.Colors.BLUE),
                        ft.Text(title, size=16, weight="bold"),
                        ft.Text(value, size=24, weight="bold", color=ft.Colors.BLUE_GREY),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
                width=250,
                height=150,
            )
        )

    def load_data(self):
        products = list_products()
        payments = self.payment_controller.get_all_payments()

        # Metrics
        total_inventory_value = sum(p.price * p.quantity for p in products)
        total_revenue = sum(p.amount for p in payments if p.status == PaymentStatus.COMPLETED)
        low_stock_count = sum(1 for p in products if p.quantity < 5)

        # Update Metric Cards
        metrics_row = self.content.controls[2]
        metrics_row.controls[0].content.content.controls[2].value = f"${total_inventory_value:,.2f}"
        metrics_row.controls[1].content.content.controls[2].value = f"${total_revenue:,.2f}"
        metrics_row.controls[2].content.content.controls[2].value = str(low_stock_count)

        # Pie Chart Data (Top 5 products by quantity)
        sorted_products = sorted(products, key=lambda p: p.quantity, reverse=True)[:5]
        pie_chart = self.content.controls[4].controls[0].content.controls[1]
        
        colors = [ft.Colors.BLUE, ft.Colors.GREEN, ft.Colors.ORANGE, ft.Colors.RED, ft.Colors.PURPLE]
        pie_chart.sections = [
            ft.PieChartSection(
                value=p.quantity,
                title=f"{p.quantity}",
                color=colors[i % len(colors)],
                radius=100,
                title_style=ft.TextStyle(size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ) for i, p in enumerate(sorted_products)
        ]

        # Bar Chart Data (Recent 5 payments)
        recent_payments = payments[:5] # Assuming get_all_payments returns ordered by date desc
        # We need to reverse them to show chronological order left to right if we want, 
        # but usually recent on right is fine or just recent 5 bars.
        # Let's show them as they come (most recent first) or maybe reverse for the chart.
        # Let's reverse to show oldest of the 5 on the left.
        recent_payments_reversed = recent_payments[::-1]
        
        bar_chart = self.content.controls[4].controls[1].content.controls[1]
        
        bar_groups = []
        for i, payment in enumerate(recent_payments_reversed):
            bar_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=payment.amount,
                            width=30,
                            color=ft.Colors.CYAN,
                            tooltip=f"${payment.amount:.2f}\n{payment.created_at.strftime('%Y-%m-%d')}",
                            border_radius=5,
                        )
                    ]
                )
            )
            
        bar_chart.bar_groups = bar_groups
        
        # Adjust axis
        if recent_payments:
            max_amount = max(p.amount for p in recent_payments)
            bar_chart.max_y = max_amount * 1.2
        
        bar_chart.bottom_axis.labels = [
            ft.ChartAxisLabel(value=i, label=ft.Text(p.created_at.strftime("%H:%M"), size=10))
            for i, p in enumerate(recent_payments_reversed)
        ]

        if self.page:
            self.update()
