# Final Pre-GitHub Audit & Quality Report: Customer Intelligence Platform

**Date**: September 3, 2026
**Auditor**: Senior Data Architect & Principal ML Engineer
**Repository Target**: `https://github.com/pratikmalik/Customer-Intelligence-Platform.git`
**Execution Constraint**: Audit and pre-commit cleanup only. **No git commit or git push executed.**

---

## A. Changes Made

1. **Repository Cleanup**:
   - Removed temporary helper script `src/add_month_number.py` after ensuring its transformation logic was fully integrated into `src/explainability.py`.
   - Confirmed zero temporary files, `.env` files, API keys, `.log` files, or local virtual environments in the git tree.
2. **License Added**:
   - Added standard, professional MIT `LICENSE` attributed to Pratik Malik (2026).
3. **Professional Documentation Alignment (`README.md`)**:
   - Eliminated unsubstantiated buzzwords ("state-of-the-art", "production-grade", "enterprise-ready").
   - Added Section 11 detailing model limitations, prototype target leakage context, and synthetic CLV formulation.
   - Reframed cohort analytics as "Monthly Purchase Participation by Cohort".
   - Verified that zero `file://` local links or Windows absolute paths exist in the documentation.

---

## B. Metrics Verified & Re-Calculated from Source

Every core project metric was re-computed directly from the underlying data and Python model pipelines:

| Metric | Specification Target | Reproduced Reality | Verification Status |
| :--- | :--- | :--- | :---: |
| **Customer Population** | 10,000 | 10,000 unique records (`customer_profiles.csv`) | 🟢 Verified Exact |
| **Transactions / Orders**| 60,597 | 60,597 transactions (`customer_transactions.csv`) | 🟢 Verified Exact |
| **Gross Revenue** | $4,822,769.79 | $4,822,769.79 (`SUM(order_amount)`) | 🟢 Verified Exact |
| **Average Order Value** | $79.59 | $79.59 (`$4,822,769.79 / 60,597`) | 🟢 Verified Exact |
| **Overall Churn Rate** | 47.81% | 47.81% (4,781 churned / 5,219 active accounts) | 🟢 Verified Exact |
| **At-Risk Revenue** | $1,304,190.87 | $1,304,190.87 (High-Risk tier spend) | 🟢 Verified Exact |
| **Avg Predicted 12M CLV**| $299.16 | $299.16 (`MEAN(predicted_12m_clv)`) | 🟢 Verified Exact |
| **Portfolio 12M CLV** | $2,991,598.37 | $2,991,598.37 (`SUM(predicted_12m_clv)`) | 🟢 Verified Exact |
| **Churn ROC-AUC** | 98.19% | 98.19% (Logistic Regression on stratified test set) | 🟢 Verified Exact |
| **Churn F1-Score** | 0.9107 | 0.9107 (Logistic Regression on test set) | 🟢 Verified Exact |
| **CLV Regression R²** | 0.9540 | 0.9540 (Random Forest Regressor, test set) | 🟢 Verified Exact |
| **CLV Regression MAE** | $29.30 | $29.30 (Random Forest Regressor, test set) | 🟢 Verified Exact |
| **CLV Regression RMSE** | $86.39 | $86.39 (Random Forest Regressor, test set) | 🟢 Verified Exact |
| **K-Means Silhouette** | 0.2236 | 0.2236 (Standardized RFM features, k=5) | 🟢 Verified Exact |

---

## C. Page 2 Dashboard Defect Resolution: "High-Risk Customer Action List"

### Defect Description
In the Page 2 table visual, individual customers belonging to the *Champions* segment were all displaying the identical values:
- `Historical Spend ($) = 19,65,147.92`
- `Support Tickets = 1.47`

### Technical Forensic Cause
Inspection of `Report/definition/pages/01c12155c4cefd5fcc19/visuals/b7f7797f3d77d5618158/visual.json` revealed:
```json
"field": {
  "Column": {
    "Expression": {
      "SourceRef": {
        "Entity": "Fact_Transactions"
      }
    },
    "Property": "customer_id"
  }
}
```
1. `Customer ID` was dragged from **`Fact_Transactions`** rather than the dimension table **`Dim_Customer_Analytics`**.
2. The data model relationship is a single-direction filter from `Dim_Customer_Analytics` (1) to `Fact_Transactions` (*).
3. Therefore, `Fact_Transactions.customer_id` **cannot filter** `Dim_Customer_Analytics`.
4. As a result, `Dim_Customer_Analytics[monetary]` was aggregated across the only active filter it could see: `rfm_segment = 'Champions'`.
5. `$1,965,147.92` is the cumulative spend of **all 1,863 Champions combined**, and `1.47` is the segment-wide average support ticket count.

### Ground-Truth Customer Verification
Looking up individual customer records directly in `Dim_Customer_Analytics` (`data/clv_predictions.csv`):
- **`CUST-10009`**: Segment = `Champions` | Churn Risk = `0.00%` | Actual Spend = **`$1,076.76`** | Support Tickets = **`0`**
- **`CUST-10012`**: Segment = `Champions` | Churn Risk = `0.19%` | Actual Spend = **`$812.29`** | Support Tickets = **`1`**
- **`CUST-10020`**: Segment = `Champions` | Churn Risk = `0.15%` | Actual Spend = **`$639.98`** | Support Tickets = **`1`**
- **`CUST-10029`**: Segment = `Champions` | Churn Risk = `0.07%` | Actual Spend = **`$823.17`** | Support Tickets = **`2`**
- **`CUST-10034`**: Segment = `Champions` | Churn Risk = `0.15%` | Actual Spend = **`$521.44`** | Support Tickets = **`2`**

### Action Required in Power BI Desktop
1. Select the **High-Risk Customer Action List** table on Page 2.
2. In the **Columns** well, remove `customer_id` (from `Fact_Transactions`).
3. Drag `customer_id` from **`Dim_Customer_Analytics`** into the first column.
4. Ensure `Historical Spend` uses `Dim_Customer_Analytics[monetary]` (Sum) and `Support Tickets` uses `Dim_Customer_Analytics[support_tickets_opened]` (Average/Don't Summarize).
5. Sort by `Churn Risk %` **Descending** so that genuine high-risk customers appear at the top.

---

## D. Methodological & Model Limitations

1. **Target Leakage in Churn Prototype**:
   - `is_churned` is defined as `recency_days > 120`.
   - `R_Score` (quantile of `recency_days`) and `rfm_total_score` were included in the prototype feature set.
   - This accounts for the high ROC-AUC (98.19%).
   - *Production Solution*: Time-slice data into observation windows ($T_{-90}$ to $T_0$) and outcome windows ($T_0$ to $T_{+90}$) without contemporaneous recency features.
2. **Synthetic Target Formulation in CLV**:
   - `target_12m_clv` was computed formulaically from annualized spend, tenure, and engagement multipliers.
   - The Random Forest regressor ($R^2 = 0.954$) learns this parametric formula.
   - Accurately presented as a "Synthetic Customer-Value Run-Rate Estimation Prototype".
3. **Cohort Metrics Definition**:
   - Month 0 baseline begins at ~11.3%–19.5% because it records calendar-month purchase participation after signup, rather than subscription survival from an acquired base.
   - Accurately titled "Monthly Repeat Purchase Participation by Cohort".
4. **Explainable AI Divergence**:
   - Tree split importance is dominated by `R_Score` (57.1%) and `rfm_total_score` (21.1%).
   - Support tickets (0.42% model split) serve as an **actionable operational intervention trigger**, whereas recency acts as the **mathematical proxy of abandonment**.

---

## E. Files Removed
- `src/add_month_number.py` (Redundant utility script; logic integrated into `src/explainability.py`).

## F. Files Added / Updated
- `LICENSE` (MIT License, Pratik Malik 2026).
- `FINAL_PROJECT3_AUDIT.md` (This comprehensive audit report).
- `README.md` (Completely overhauled to senior industry standards).

## G. Tests Executed
- `python src/test_api.py` (5/5 integration tests passed: `/health`, `/predict/churn`, `/predict/clv`, `/predict/profile`).
- `python src/rfm_segmentation.py` (Pass, validated Silhouette score 0.2236).
- `python src/churn_prediction.py` (Pass, validated ROC-AUC 98.19%, F1 0.9107).
- `python src/clv_estimation.py` (Pass, validated R² 0.9540, MAE $29.30).
- `python src/explainability.py` (Pass, regenerated XAI and cohort data).

---

## H. Remaining Steps for the User

1. In Power BI Desktop: On Page 2, replace `Fact_Transactions[customer_id]` with `Dim_Customer_Analytics[customer_id]` in the table visual.
2. Save the Power BI report (`Ctrl + S`).
3. You are ready to run `git init`, `git add .`, `git commit`, and `git push` to your repository.
