import flet as ft
from controllers.inventory import list_products, add_product, remove_product
from models.item import Product
from utils.theme import AppColors

class ProductSection(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 20
        
        self.products = list_products()
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Category")),
                ft.DataColumn(ft.Text("Price")),
                ft.DataColumn(ft.Text("Cost")),
                ft.DataColumn(ft.Text("Quantity")),
                ft.DataColumn(ft.Text("In Stock")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            rows=[],
        )
        
        # Initial load of products
        self.load_products()

        self.name_field = ft.TextField(label="Name")
        self.category_field = ft.TextField(label="Category")
        self.price_field = ft.TextField(label="Price", keyboard_type=ft.KeyboardType.NUMBER)
        self.cost_field = ft.TextField(label="Cost Price", keyboard_type=ft.KeyboardType.NUMBER)
        self.quantity_field = ft.TextField(label="Quantity", keyboard_type=ft.KeyboardType.NUMBER)
        
        self.add_dialog = ft.AlertDialog(
            title=ft.Text("Add Product"),
            content=ft.Column([
                self.name_field,
                self.category_field,
                self.price_field,
                self.cost_field,
                self.quantity_field
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.TextButton("Add", on_click=self.save_product),
            ],
        )

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Inventory", size=30, weight="bold"),
                        ft.ElevatedButton("Add Product", icon=ft.Icons.ADD, on_click=self.open_add_dialog)
                    ], 
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Container(
                    content=ft.Column([self.data_table], scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    padding=10
                ),
            ],
            expand=True,
        )

    def load_products(self):
        self.products = list_products()
        self.data_table.rows = [self.create_row(p) for p in self.products]
        if self.page:
            self.update()

    def create_row(self, product: Product):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(product.name)),
                ft.DataCell(ft.Text(product.category or "-")),
                ft.DataCell(ft.Text(f"${product.price:.2f}")),
                ft.DataCell(ft.Text(f"${product.cost_price:.2f}")),
                ft.DataCell(ft.Text(str(product.quantity))),
                ft.DataCell(ft.Icon(ft.Icons.CHECK_CIRCLE if product.in_stock else ft.Icons.CANCEL, color=AppColors.SUCCESS if product.in_stock else AppColors.ERROR)),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(ft.Icons.DELETE, icon_color=AppColors.ERROR, on_click=lambda e: self.delete_product_click(product)),
                    ])
                ),
            ]
        )

    def open_add_dialog(self, e):
        self.page.open(self.add_dialog)

    def close_dialog(self, e):
        self.page.close(self.add_dialog)

    def save_product(self, e):
        try:
            name = self.name_field.value
            category = self.category_field.value
            price = float(self.price_field.value)
            cost = float(self.cost_field.value or 0.0)
            quantity = int(self.quantity_field.value)
            
            new_product = Product(
                name=name,
                category=category,
                price=price,
                cost_price=cost,
                quantity=quantity,
                in_stock=quantity > 0
            )
            add_product(new_product)
            self.close_dialog(e)
            self.load_products()
            self.name_field.value = ""
            self.category_field.value = ""
            self.price_field.value = ""
            self.cost_field.value = ""
            self.quantity_field.value = ""
            
            self.page.open(ft.SnackBar(content=ft.Text("Product added successfully!")))
            
        except ValueError:
            self.page.open(ft.SnackBar(content=ft.Text("Invalid input! Please check price and quantity.")))

    def delete_product_click(self, product: Product):
        remove_product(product.id)
        self.load_products()
        self.page.open(ft.SnackBar(content=ft.Text("Product deleted!")))
