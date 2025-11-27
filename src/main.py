import flet as ft
from db.conn import init_db
from components.product_section import ProductSection

def main(page: ft.Page):
    page.title = "HyperSpin"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Initialize Database
    init_db()

    page.add(
        ft.SafeArea(
            ProductSection(),
            expand=True,
        )
    )

ft.app(main)
