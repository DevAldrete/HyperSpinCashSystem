import flet as ft
from utils.theme import AppColors, AppTextStyles, AppSpacing
from controllers.analytics import AnalyticsService
from controllers.inventory import list_products
import csv
import io
from datetime import datetime

class ReportSection(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = AppSpacing.MEDIUM
        self.analytics = AnalyticsService()
        
        self.tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Sales Report", content=self._build_sales_tab()),
                ft.Tab(text="Inventory Report", content=self._build_inventory_tab()),
            ],
            expand=True,
        )
        
        self.content = ft.Column(
            [
                ft.Text("Reports & Export", style=AppTextStyles.HEADER_LARGE),
                self.tabs
            ],
            expand=True
        )

    def _build_sales_tab(self):
        self.sales_data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Date")),
                ft.DataColumn(ft.Text("Total")),
                ft.DataColumn(ft.Text("Status")),
            ],
            rows=[]
        )
        
        return ft.Column(
            [
                ft.Row([
                    ft.ElevatedButton("Export CSV", icon=ft.Icons.DOWNLOAD, on_click=self.export_sales_csv)
                ]),
                ft.Container(
                    content=ft.Column([self.sales_data_table], scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    border=ft.border.all(1, AppColors.BORDER),
                    border_radius=5,
                )
            ],
            expand=True,
            spacing=AppSpacing.MEDIUM,
            run_spacing=AppSpacing.MEDIUM,
        )

    def _build_inventory_tab(self):
        self.inventory_data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Category")),
                ft.DataColumn(ft.Text("Price")),
                ft.DataColumn(ft.Text("Stock")),
                ft.DataColumn(ft.Text("Value")),
            ],
            rows=[]
        )
        
        return ft.Column(
            [
                ft.Row([
                    ft.ElevatedButton("Export CSV", icon=ft.Icons.DOWNLOAD, on_click=self.export_inventory_csv)
                ]),
                ft.Container(
                    content=ft.Column([self.inventory_data_table], scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    border=ft.border.all(1, AppColors.BORDER),
                    border_radius=5,
                )
            ],
            expand=True,
            spacing=AppSpacing.MEDIUM,
            run_spacing=AppSpacing.MEDIUM,
        )

    def did_mount(self):
        self.file_picker = ft.FilePicker(on_result=self.on_save_file_result)
        self.page.overlay.append(self.file_picker)
        self.page.update()
        self.load_data()

    def load_data(self):
        # Load Inventory
        products = list_products()
        self.inventory_data_table.rows = []
        for p in products:
            self.inventory_data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(p.name)),
                        ft.DataCell(ft.Text(p.category or "-")),
                        ft.DataCell(ft.Text(f"${p.price:.2f}")),
                        ft.DataCell(ft.Text(str(p.quantity))),
                        ft.DataCell(ft.Text(f"${p.price * p.quantity:.2f}")),
                    ]
                )
            )
            
        # Load Sales (Recent 50 for now)
        sales = self.analytics.get_recent_sales(limit=50)
        self.sales_data_table.rows = []
        for s in sales:
            self.sales_data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(s.created_at.strftime("%Y-%m-%d %H:%M"))),
                        ft.DataCell(ft.Text(f"${s.total_amount:.2f}")),
                        ft.DataCell(ft.Text(s.status)),
                    ]
                )
            )
        
        if self.page:
            self.update()

    def export_sales_csv(self, e):
        self.current_export = "sales"
        self.file_picker.save_file(file_name="sales_report.csv")

    def export_inventory_csv(self, e):
        self.current_export = "inventory"
        self.file_picker.save_file(file_name="inventory_report.csv")

    def on_save_file_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            try:
                if self.current_export == "sales":
                    self._write_sales_csv(e.path)
                elif self.current_export == "inventory":
                    self._write_inventory_csv(e.path)
                
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Saved to {e.path}"), bgcolor=AppColors.SUCCESS))
            except Exception as ex:
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error saving file: {ex}"), bgcolor=AppColors.ERROR))

    def _write_sales_csv(self, path):
        sales = self.analytics.get_recent_sales(limit=1000) # Fetch more for export
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Date", "Total Amount", "Status"])
            for s in sales:
                writer.writerow([s.id, s.created_at, s.total_amount, s.status])

    def _write_inventory_csv(self, path):
        products = list_products()
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Category", "Price", "Cost", "Quantity", "In Stock"])
            for p in products:
                writer.writerow([p.id, p.name, p.category, p.price, p.cost_price, p.quantity, p.in_stock])
