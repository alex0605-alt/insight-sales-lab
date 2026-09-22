-- 1. Tendencia mensual de ingresos, utilidad y margen.
SELECT
    d.year,
    d.month,
    ROUND(SUM(f.net_sales), 2) AS net_revenue,
    ROUND(SUM(f.gross_profit), 2) AS gross_profit,
    ROUND(100.0 * SUM(f.gross_profit) / NULLIF(SUM(f.net_sales), 0), 2) AS gross_margin_pct
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- 2. Productos con ventas relevantes y margen inferior al promedio.
WITH product_performance AS (
    SELECT
        p.product,
        p.category,
        SUM(f.net_sales) AS revenue,
        100.0 * SUM(f.gross_profit) / NULLIF(SUM(f.net_sales), 0) AS margin_pct
    FROM fact_sales f
    JOIN dim_product p ON p.product_key = f.product_key
    GROUP BY p.product, p.category
)
SELECT *
FROM product_performance
WHERE margin_pct < (SELECT AVG(margin_pct) FROM product_performance)
ORDER BY revenue DESC;

-- 3. Comparación regional y tasa de devoluciones.
SELECT
    s.region,
    ROUND(SUM(f.net_sales), 2) AS net_revenue,
    ROUND(AVG(f.returned) * 100, 2) AS return_rate_pct,
    COUNT(DISTINCT f.order_id) AS orders
FROM fact_sales f
JOIN dim_store s ON s.store_key = f.store_key
GROUP BY s.region
ORDER BY net_revenue DESC;
