import flet as ft
from controllers.inventory import list_products
from controllers.payment import PaymentController
from models.item import Product
from models.payment import PaymentMethod
from utils.logger import get_logger
from typing import Dict, Any

logger = get_logger()

class PaymentSection(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10
        self.payment_controller = PaymentController()
        
        # Cart state: {product_id: {'product': Product, 'quantity': int}}
        self.cart: Dict[str, Dict[str, Any]] = {}
        
        # UI Components
        self.products_grid = ft.GridView(
            expand=True,
            runs_count=5,
            max_extent=200,
            child_aspect_ratio=1.0,
            spacing=10,
            run_spacing=10,
        )
        
        self.cart_list = ft.ListView(expand=True, spacing=10)
        self.total_text = ft.Text("Total: $0.00", size=24, weight="bold")
        self.dialog_total_text = ft.Text("Total: $0.00", size=24, weight="bold") # Separate control for dialog

        self.pay_button = ft.ElevatedButton(
            "Pay", 
            icon=ft.Icons.PAYMENT, 
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
            on_click=self.open_payment_dialog,
            disabled=True
        )
        
        # Payment Dialog Components
        self.amount_received_field = ft.TextField(
            label="Amount Received", 
            prefix_text="$", 
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self.calculate_change
        )
        self.change_text = ft.Text("Change: $0.00", size=20, weight="bold")
        self.payment_dialog = ft.AlertDialog(
            title=ft.Text("Process Payment"),
            content=ft.Column([
                ft.Text("Total Amount:", size=16),
                self.dialog_total_text, 
                ft.Divider(),
                self.amount_received_field,
                self.change_text
            ], tight=True, width=400),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_payment_dialog),
                ft.ElevatedButton("Confirm Payment", on_click=self.process_payment)
            ],
        )

        # Main Layout
        self.content = ft.Row(
            [
                # Left Side: Products
                ft.Container(
                    content=ft.Column([
                        ft.Text("Available Products", size=24, weight="bold"),
                        self.products_grid
                    ]),
                    expand=7,
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                ),
                # Right Side: Cart
                ft.Container(
                    content=ft.Column([
                        ft.Text("Current Order", size=24, weight="bold"),
                        ft.Divider(),
                        self.cart_list,
                        ft.Divider(),
                        ft.Row([self.total_text], alignment=ft.MainAxisAlignment.END),
                        ft.Container(height=10),
                        ft.Row([self.pay_button], alignment=ft.MainAxisAlignment.CENTER)
                    ]),
                    expand=3,
                    padding=20,
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    border_radius=10,
                )
            ],
            expand=True
        )
        
        self.load_products()

    def load_products(self):
        logger.info("Loading products for PaymentSection")
        products = list_products()
        self.products_grid.controls = []
        for product in products:
            if product.in_stock and product.quantity > 0:
                self.products_grid.controls.append(self.create_product_card(product))
        if self.page:
            self.update()

    def create_product_card(self, product: Product):
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.SHOPPING_BAG, size=40, color=ft.Colors.BLUE),
                ft.Text(product.name, weight="bold", size=16, text_align="center"),
                ft.Text(f"${product.price:.2f}", size=14),
                ft.Text(f"Stock: {product.quantity}", size=12, color=ft.Colors.GREY),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=10,
            ink=True,
            on_click=lambda e: self.add_to_cart(product),
            border=ft.border.all(1, ft.Colors.BLUE_100)
        )

    def add_to_cart(self, product: Product):
        pid = str(product.id)
        if pid in self.cart:
            if self.cart[pid]['quantity'] < product.quantity:
                self.cart[pid]['quantity'] += 1
            else:
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Max stock reached for {product.name}")))
                return
        else:
            self.cart[pid] = {'product': product, 'quantity': 1}
        
        self.update_cart_ui()

    def remove_from_cart(self, product_id: str):
        if product_id in self.cart:
            del self.cart[product_id]
            self.update_cart_ui()

    def update_quantity(self, product_id: str, delta: int):
        if product_id in self.cart:
            new_qty = self.cart[product_id]['quantity'] + delta
            product = self.cart[product_id]['product']
            
            if new_qty <= 0:
                self.remove_from_cart(product_id)
            elif new_qty <= product.quantity:
                self.cart[product_id]['quantity'] = new_qty
                self.update_cart_ui()
            else:
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Max stock reached for {product.name}")))

    def update_cart_ui(self):
        self.cart_list.controls = []
        total = 0.0
        
        for pid, item in self.cart.items():
            product = item['product']
            qty = item['quantity']
            line_total = product.price * qty
            total += line_total
            
            self.cart_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(product.name, weight="bold", max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(f"${product.price:.2f}", size=12, color=ft.Colors.GREY),
                        ], expand=True),
                        
                        ft.Row([
                            ft.IconButton(ft.Icons.REMOVE, icon_size=18, on_click=lambda e, pid=pid: self.update_quantity(pid, -1), style=ft.ButtonStyle(padding=0)),
                            ft.Text(f"{qty}", weight="bold", size=14),
                            ft.IconButton(ft.Icons.ADD, icon_size=18, on_click=lambda e, pid=pid: self.update_quantity(pid, 1), style=ft.ButtonStyle(padding=0)),
                        ], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
                        
                        ft.Text(f"${line_total:.2f}", weight="bold", size=14, width=70, text_align=ft.TextAlign.RIGHT),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=5,
                    border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.GREY_300))
                )
            )
            
        self.total_text.value = f"Total: ${total:.2f}"
        self.pay_button.disabled = len(self.cart) == 0
        self.update()

    def open_payment_dialog(self, e):
        logger.info("Opening payment dialog")
        self.dialog_total_text.value = self.total_text.value
        self.amount_received_field.value = ""
        self.change_text.value = "Change: $0.00"
        self.page.open(self.payment_dialog)

    def close_payment_dialog(self, e):
        self.page.close(self.payment_dialog)

    def calculate_change(self, e):
        try:
            total = sum(item['product'].price * item['quantity'] for item in self.cart.values())
            received = float(self.amount_received_field.value)
            change = received - total
            self.change_text.value = f"Change: ${change:.2f}"
            self.change_text.color = ft.Colors.GREEN if change >= 0 else ft.Colors.RED
            self.update()
        except ValueError:
            self.change_text.value = "Change: $0.00"
            self.update()

    def process_payment(self, e):
        try:
            total = sum(item['product'].price * item['quantity'] for item in self.cart.values())
            received = float(self.amount_received_field.value)
            
            if received < total:
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Insufficient amount received!")))
                return

            items_to_process = [
                {'product_id': item['product'].id, 'quantity': item['quantity']}
                for item in self.cart.values()
            ]
            
            logger.info(f"Processing payment for {len(items_to_process)} items. Total: {total}")
            
            payment = self.payment_controller.create_payment(
                items=items_to_process,
                payment_method=PaymentMethod.CASH # Defaulting to CASH for now
            )
            
            logger.info(f"Payment successful: {payment.id}")
            
            self.close_payment_dialog(e)
            self.cart.clear()
            self.update_cart_ui()
            self.load_products() # Refresh stock
            
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Payment successful!"), bgcolor=ft.Colors.GREEN))
            
        except ValueError as ve:
            logger.error(f"Payment validation error: {ve}")
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(str(ve)), bgcolor=ft.Colors.RED))
        except Exception as ex:
            logger.exception(f"Payment processing failed: {ex}")
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("An error occurred during payment."), bgcolor=ft.Colors.RED))
