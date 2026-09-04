# Power BI 5-Page Dashboard Specification — Customer Intelligence Platform

This document serves as the complete architectural design blueprint for constructing the interactive **5-Page Power BI Customer Intelligence, Churn & Lifetime Value Dashboard**.

---

## 🏗️ 1. Data Model & Extended Star Schema Architecture

### Fact Tables
1. **Fact_Transactions** (data/customer_transactions.csv)
   - 	ransaction_id (PK)
   - customer_id (FK)
   - 	ransaction_date
   - order_amount
   - items_count
   - shipping_delay_days
   - is_returned

2. **Fact_Cohort_Retention** (data/cohort_retention_matrix.csv)
   - signup_quarter
   - Cohort_Size
   - Retention_Month (Month_0 to Month_12)
   - Retention_Rate_Pct

### Dimension Tables
1. **Dim_Customer_Analytics** (data/clv_predictions.csv)
   - customer_id (PK)
   -
fm_segment
   - kmeans_cluster
   - is_churned
   - churn_probability
   -
isk_tier
   - predicted_12m_clv
   - clv_tier
   - country
   - cquisition_channel
   - support_tickets_opened
   - email_open_rate

2. **Dim_Churn_Drivers** (data/churn_driver_analysis.csv)
   - eature_name (PK)
   - importance_weight
   -
elative_impact_pct
   - usiness_description
   - driver_type (Operational Friction, Customer Engagement, Financial)

3. **Dim_Date** (Generated in Power BI via DAX CALENDARAUTO())

### Relationships
- Dim_Customer_Analytics[customer_id] 1 : N Fact_Transactions[customer_id] (Single direction filter)
- Dim_Date[Date] 1 : N Fact_Transactions[transaction_date]

---

## 🧮 2. Key DAX Measures (Pages 1 to 5)

`dax
// ================= PAGE 1 MEASURES =================
Total Active Customers =
CALCULATE(
    COUNTROWS(Dim_Customer_Analytics),
    Dim_Customer_Analytics[is_churned] = 0
)

Total Churned Customers =
CALCULATE(
    COUNTROWS(Dim_Customer_Analytics),
    Dim_Customer_Analytics[is_churned] = 1
)

Churn Rate % =
DIVIDE(
    [Total Churned Customers],
    COUNTROWS(Dim_Customer_Analytics),
    0
)

Total Revenue = SUM(Fact_Transactions[order_amount])

Avg Predicted 12M CLV = AVERAGE(Dim_Customer_Analytics[predicted_12m_clv])

Portfolio 12M Future Value = SUM(Dim_Customer_Analytics[predicted_12m_clv])


// ================= PAGE 2 MEASURES =================
At Risk Revenue =
CALCULATE(
    SUM(Dim_Customer_Analytics[monetary]),
    Dim_Customer_Analytics[risk_tier] = "High Risk"
)

High Risk VIP Count =
CALCULATE(
    COUNTROWS(Dim_Customer_Analytics),
    Dim_Customer_Analytics[risk_tier] = "High Risk",
    Dim_Customer_Analytics[rfm_segment] IN {"Champions", "Loyal Customers"}
)


// ================= PAGE 4 MEASURES (XAI & DRIVERS) =================
Top Churn Driver % =
MAXX(
    TOPN(1, Dim_Churn_Drivers, Dim_Churn_Drivers[relative_impact_pct], DESC),
    Dim_Churn_Drivers[relative_impact_pct]
)

Operational Friction Drivers Count =
CALCULATE(
    COUNTROWS(Dim_Churn_Drivers),
    Dim_Churn_Drivers[driver_type] = "Operational Friction"
)

High Ticket Churn Rate =
CALCULATE(
    AVERAGE(Dim_Customer_Analytics[churn_probability]),
    Dim_Customer_Analytics[support_tickets_opened] >= 3
)


// ================= PAGE 5 MEASURES (COHORTS) =================
Avg 12M Cohort Retention % =
CALCULATE(
    AVERAGE(Fact_Cohort_Retention[Retention_Rate_Pct]),
    Fact_Cohort_Retention[Retention_Month] = "Month_12",
    Fact_Cohort_Retention[Retention_Rate_Pct] > 0
)

Total Tracked Signups =
SUM(Fact_Cohort_Retention[Cohort_Size])
`

---

## 📊 3. Complete 5-Page Layout Blueprint

### 📌 Page 1: Executive Overview (Portfolio Macro Health)
* **Top Summary Cards**: Total Active Customers (5,219), Avg Predicted 12M CLV (.16), Total Revenue (.82M), Churn Rate % (47.81%).
* **Area Chart**: Total Revenue by Year (2024 to 2025).
* **Map Visual**: Global Revenue Map (USA, UK, Canada, Germany, Australia).
* **Clustered Column Chart**: Total Revenue by Country.
* **Bar Chart**: Revenue by Acquisition Channel.
* **Treemap**: Top Product Categories by Revenue (Sports, Home & Kitchen, Beauty, Electronics, Apparel).
* **Donut Chart**: Customer Segmentation breakdown (Hibernating, Lost, Loyal, Champions, At Risk, Potential Loyalists).

---

### 📌 Page 2: Churn & Risk Analytics (Revenue at Risk)
* **Top KPI Cards**: Total Orders (60.60K), At Risk Revenue (.30M), Total Customers (10.00K).
* **Slicer**: Risk Tier (High Risk, Low Risk).
* **Funnel Chart**: Customer Lifecycle Retention Funnel.
* **Line/Area Chart**: Churn Probability Trend by Recency (Days).
* **Column Chart**: Customer Volume by Risk Tier.
* **Scatter Plot**: Recency (Days) vs Monetary Spend ($) colored by Risk Tier.
* **Actionable Customer Table**: customer_id,
fm_segment, churn_probability, monetary, support_tickets_opened.

---

### 📌 Page 3: CLV Growth Strategy (Future Value Allocation)
* **Slicers**: Acquisition_channel & Country.
* **Column Chart**: Average 12M Value by CLV Tier ($) (Tier 1 VIP +, Tier 2 -, Tier 3 -, Tier 4 <).
* **Matrix Visual**: CLV Revenue Distribution Matrix ($) (RFM Segment vs Risk Tier).
* **Horizontal Bar Chart**: Average 12M CLV by RFM Segment ($).
* **Clustered Column Chart**: Historical Spend vs Predicted 12M CLV by Acquisition Channel.

---

### 📌 Page 4: Explainable AI & Churn Drivers (Root-Cause Diagnostics)
* **Top Summary Cards**: Top Churn Driver % (57.1% Inactivity), High Ticket Churn Rate (78.4% for 3+ tickets), Operational Friction Factors (3 primary bottlenecks).
* **Horizontal Tornado / Bar Chart**: Relative Feature Importance Ranking (Dim_Churn_Drivers[business_description] vs
elative_impact_pct) colored by driver_type.
* **Line Chart**: Support Tickets vs. Predicted Churn Probability (showing sharp inflection at 3+ tickets).
* **Decomposition Tree**: Revenue at Risk broken down by driver_type -> preferred_category -> vg_shipping_delay.
* **Prescriptive Action Guide**: Card highlighting required operational SLAs (e.g. resolve support tickets under 24 hours).

---

### 📌 Page 5: Cohort Retention & Lifetime Dynamics (Customer Survival)
* **Top Summary Cards**: Avg 12M Cohort Retention % (25.5%), Peak Retention Quarter (2024-Q3), Total Signups Analyzed (10,000).
* **Matrix Heatmap**: Signup Quarter (signup_quarter) vs Retention Month (Retention_Month Month_0 to Month_12) with green-to-red conditional formatting on Retention_Rate_Pct.
* **Line Chart (Decay Curve)**: Retention Rate % over Retention Months (Month 0 through Month 12).
* **Clustered Bar Chart**: Initial Cohort Size vs 12-Month Retained Customer Count.
* **Key Milestone Callouts**: 30-Day Benchmark (25.4%), 90-Day Benchmark (28.4%), 365-Day Benchmark (25.5%).

---

## 🎯 4. Prescriptive Business Strategy Matrix (Strategic Playbook)

| Customer Segment | Churn Risk Tier | Root-Cause Driver | Recommended Retention Strategy | Strategic Objective |
| :--- | :--- | :--- | :--- | :--- |
| **Champions** | High Risk | Support Friction (3+ Tickets) | **White-Glove VIP Support + Loyalty Voucher**: Immediate CSM phone outreach. | Protect high-value VIP account base |
| **Loyal Customers** | Medium Risk | Shipping Delays (>3 Days) | **Priority Dispatch & Free Express Shipping Upgrade**: Mitigate delivery frustration. | Restore fulfillment satisfaction |
| **At Risk Spenders** | High Risk | Prolonged Inactivity (>90 Days) | **Win-Back Campaign**: Double reward points offer valid for 14 days. | Re-activate high-historical-spend buyers |
| **Hibernating** | Low / Medium Risk | Low Email Engagement (<20%) | **Subject Line Personalization & Product Discovery Push**: Highlight new category releases. | Cost-effective digital re-engagement |
