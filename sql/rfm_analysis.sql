-- ====================================================================
-- Customer Intelligence Platform - RFM Feature Extraction SQL Queries
-- Database Compatibility: SQLite, DuckDB, PostgreSQL, MySQL
-- Description: Aggregates transaction data per customer to compute Recency,
--              Frequency, Monetary (RFM) metrics and customer features.
-- ====================================================================

-- Step 1: Base Customer Aggregations
WITH CustomerAggregates AS (
    SELECT
        t.customer_id,
        MAX(t.transaction_date) AS last_purchase_date,
        MIN(t.transaction_date) AS first_purchase_date,
        COUNT(DISTINCT t.transaction_id) AS total_orders,
        SUM(t.order_amount) AS monetary_value,
        AVG(t.order_amount) AS avg_order_value,
        SUM(t.items_count) AS total_items_purchased,
        AVG(t.shipping_delay_days) AS avg_shipping_delay,
        SUM(t.is_returned) AS total_returns,
        AVG(t.discount_applied) AS avg_discount_rate
    FROM customer_transactions t
    GROUP BY t.customer_id
),

-- Step 2: Compute Recency (Days since snapshot date) and Tenure
RFM_Calculated AS (
    SELECT
        ca.customer_id,
        CAST((JULIANDAY('2026-01-01 00:00:00') - JULIANDAY(ca.last_purchase_date)) AS INTEGER) AS recency_days,
        ca.total_orders AS frequency,
        ROUND(ca.monetary_value, 2) AS monetary,
        ROUND(ca.avg_order_value, 2) AS avg_order_value,
        ca.total_items_purchased,
        ROUND(ca.avg_shipping_delay, 1) AS avg_shipping_delay,
        ca.total_returns,
        ROUND(ca.avg_discount_rate, 2) AS avg_discount_rate,
        CAST((JULIANDAY('2026-01-01 00:00:00') - JULIANDAY(p.signup_date)) AS INTEGER) AS tenure_days,
        p.acquisition_channel,
        p.country,
        p.preferred_category,
        p.support_tickets_opened,
        p.email_open_rate,
        p.app_installed
    FROM CustomerAggregates ca
    JOIN customer_profiles p ON ca.customer_id = p.customer_id
),

-- Step 3: Quantile Scoring (R_Score, F_Score, M_Score 1-5)
RFM_Scored AS (
    SELECT
        *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS R_Score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS F_Score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS M_Score
    FROM RFM_Calculated
)

-- Step 4: Final Segment Classification Query
SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,
    avg_order_value,
    R_Score,
    F_Score,
    M_Score,
    (R_Score + F_Score + M_Score) AS rfm_total_score,
    CASE
        WHEN R_Score >= 4 AND F_Score >= 4 AND M_Score >= 4 THEN 'Champions'
        WHEN R_Score >= 3 AND F_Score >= 3 AND M_Score >= 3 THEN 'Loyal Customers'
        WHEN R_Score >= 3 AND F_Score < 3 AND M_Score >= 3 THEN 'Potential Loyalists'
        WHEN R_Score < 3 AND F_Score >= 3 AND M_Score >= 3 THEN 'At Risk Spenders'
        WHEN R_Score <= 2 AND F_Score <= 2 AND M_Score <= 2 THEN 'Lost Customers'
        ELSE 'Hibernating / Needing Attention'
    END AS rfm_segment,
    tenure_days,
    acquisition_channel,
    country,
    preferred_category,
    support_tickets_opened,
    email_open_rate,
    app_installed,
    CASE WHEN recency_days > 120 THEN 1 ELSE 0 END AS is_churned
FROM RFM_Scored
ORDER BY monetary DESC;
