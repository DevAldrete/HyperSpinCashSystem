import flet as ft
from db.conn import init_db
from components.product_section import ProductSection
from components.payment_section import PaymentSection
from components.status_section import StatusSection
from components.report_section import ReportSection
from utils.logger import get_logger

logger = get_logger()

def main(page: ft.Page):
    page.title = "HyperSpin POS"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # Initialize Database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    # Initialize Sections
    payment_section = PaymentSection()
    product_section = ProductSection()
    status_section = StatusSection()
    report_section = ReportSection()

    def on_tab_change(e):
        index = e.control.selected_index
        if index == 0:
            status_section.load_data()
        elif index == 1:
            payment_section.load_products()
        elif index == 2:
            product_section.load_products()
        elif index == 3:
            report_section.load_data()

    # Tabs for navigation
    t = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        on_change=on_tab_change,
        tabs=[
            ft.Tab(
                text="Dashboard",
                icon=ft.Icons.DASHBOARD,
                content=status_section,
            ),
            ft.Tab(
                text="POS Terminal",
                icon=ft.Icons.POINT_OF_SALE,
                content=payment_section,
            ),
            ft.Tab(
                text="Inventory Management",
                icon=ft.Icons.INVENTORY,
                content=product_section,
            ),
            ft.Tab(
                text="Reports",
                icon=ft.Icons.ASSESSMENT,
                content=report_section,
            ),
        ],
        expand=True,
    )

    page.add(
        ft.SafeArea(
            t,
            expand=True,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
