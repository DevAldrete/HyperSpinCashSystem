Extend pricing and profit models
1. Add cost_price (or purchase_price) to models/item.py.
2. Introduce Sale and SaleItem models (order + line items).
3. Link Payment to Sale and add fields for discounts, tax, and created_at.

Implement analytics query layer
- Create an AnalyticsService (or similar) to compute:
    1. Inventory value, revenue, profit, low-stock counts.
    2. Stock distribution (top N products).
    3. Aggregations by day/week/month.

Refactor StatusSection to use analytics
1. Replace direct list_products() and PaymentController calls with AnalyticsService calls.
2. Feed the metric cards, pie chart, and bar chart from the analytics results.

Add time-based filters to dashboard
1. Add a dropdown/segmented control (Today / Last 7 days / This month / Custom).
2. Wire it so changing the period refreshes metrics and charts using AnalyticsService.

Add profit and margin metrics
1. Compute gross profit and profit margin (overall and by selected period).
2. Add new metric cards such as “Total Profit” and “Avg Margin %”.

Introduce product category support
1. Add Category model or a category field in Item.
2. Update inventory UI to assign categories.
3. Adjust analytics to allow grouping by category (even if UI comes later).

Enhance payments classification
1. Extend Payment with a type/method field (cash, card, refund, etc.).
2. Update payment creation flows to set this.
3. Add analytics helpers to filter/sum by payment type.

Improve dashboard interactivity and navigation
1. Make metric cards clickable (e.g., open low-stock view on click).
2. Organize app into clear sections: Dashboard, Inventory, Sales, Settings.

Centralize theming and styling 
1. Create utils/theme.py for colors, typography, spacing.
2. Replace hard-coded ft.Colors.* in components (like StatusSection) with theme constants.

Add loading, empty, and error states
1. Show progress indicators while loading dashboard data.
2. Show “No data yet” for empty charts/tables.
3. Handle DB/logic errors with friendly messages instead of silent failures.

Strengthen authentication and authorization
1. Define roles (admin, cashier, inventory manager).
2. Enforce permissions in controllers and critical views (price changes, profit analytics, exports).

Implement basic reporting and export
1. Add simple “Sales report” and “Inventory report” screens with filters for date range and category.
2. Implement CSV/Excel export for selected filters.

Add test coverage for core logic
1. Set up pytest (if not already).
2. Write tests for: profit calculations, low-stock detection, time-based aggregations.

Create seed/demo data scripts
1. Add a script to populate demo items, categories, sales, and payments.
2. Use it in development to see realistic dashboards and verify analytics.

Optimize database queries and indexing
1. Move heavy aggregations into SQL (group-by, sum) via SQLModel.
2. Add indexes on created_at, status, and foreign keys for SaleItem / Payment.