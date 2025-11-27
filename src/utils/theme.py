import flet as ft

class AppColors:
    PRIMARY = ft.Colors.BLUE
    SECONDARY = ft.Colors.ORANGE
    BACKGROUND = ft.Colors.WHITE
    SURFACE = ft.Colors.GREY_100
    ERROR = ft.Colors.RED
    SUCCESS = ft.Colors.GREEN
    WARNING = ft.Colors.AMBER
    
    TEXT_PRIMARY = ft.Colors.BLACK
    TEXT_SECONDARY = ft.Colors.GREY_700
    TEXT_INVERSE = ft.Colors.WHITE
    
    DIVIDER = ft.Colors.GREY_400
    BORDER = ft.Colors.GREY_400
    GRID_LINES = ft.Colors.GREY_300
    
    BACKGROUND_VARIANT = ft.Colors.BLUE_GREY_50
    SURFACE_VARIANT = ft.Colors.BLUE_50
    BORDER_LIGHT = ft.Colors.BLUE_100
    
    # Chart colors
    CHART_1 = ft.Colors.BLUE
    CHART_2 = ft.Colors.GREEN
    CHART_3 = ft.Colors.ORANGE
    CHART_4 = ft.Colors.RED
    CHART_5 = ft.Colors.PURPLE
    CHART_BAR = ft.Colors.CYAN
    
    TOOLTIP_BG = ft.Colors.with_opacity(0.5, ft.Colors.GREY_300)

class AppTextStyles:
    HEADER_LARGE = ft.TextStyle(size=30, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY)
    HEADER_MEDIUM = ft.TextStyle(size=24, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY)
    HEADER_SMALL = ft.TextStyle(size=20, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY)
    BODY_DEFAULT = ft.TextStyle(size=16, color=AppColors.TEXT_PRIMARY)
    LABEL_BOLD = ft.TextStyle(size=16, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY)
    METRIC_VALUE = ft.TextStyle(size=24, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY)
    CHART_LABEL = ft.TextStyle(size=12, color=AppColors.TEXT_INVERSE, weight=ft.FontWeight.BOLD)

class AppSpacing:
    XS = 5
    SMALL = 10
    MEDIUM = 20
    LARGE = 30
    XL = 40
