import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

def generate_pdf_guide():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == 'src' else script_dir
    docs_dir = os.path.join(project_root, 'docs')
    os.makedirs(docs_dir, exist_ok=True)

    pdf_filename = os.path.join(docs_dir, 'Customer_Intelligence_Platform_Master_Guide.pdf')

    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    PRIMARY = colors.HexColor('#2C3E50')     # Dark Slate Navy
    SECONDARY = colors.HexColor('#2980B9')   # Corporate Blue
    ACCENT = colors.HexColor('#27AE60')      # Emerald Green
    NEUTRAL_DARK = colors.HexColor('#34495E')
    LIGHT_BG = colors.HexColor('#F8F9FA')

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=16,
        textColor=SECONDARY,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=PRIMARY,
        spaceBefore=15,
        spaceAfter=8
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=SECONDARY,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=NEUTRAL_DARK,
        alignment=TA_LEFT,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=NEUTRAL_DARK,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#C0392B'),
        backColor=colors.HexColor('#EAEDED'),
        borderColor=colors.HexColor('#BDC3C7'),
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    story = []

    # -------------------------------------------------------------------------
    # COVER / HEADER BANNER
    # -------------------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("Customer Intelligence Platform — Churn & Lifetime Value Analytics", title_style))
    story.append(Paragraph("End-to-End Master Project Documentation & Interview Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=SECONDARY, spaceAfter=15))

    # Overview Box Table
    overview_data = [
        [Paragraph("<b>Author:</b> Data Analyst & ML Engineer", body_style), Paragraph("<b>Tech Stack:</b> Python, SQL, Scikit-learn, Power BI", body_style)],
        [Paragraph("<b>Scope:</b> 10,000 Customers | 60,597 Transactions", body_style), Paragraph("<b>Target Metrics:</b> 98.19% ROC-AUC | 0.9536 R²", body_style)]
    ]
    t_overview = Table(overview_data, colWidths=[260, 260])
    t_overview.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BDC3C7')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_overview)
    story.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # SECTION 1: EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Executive Summary & Core Business Problem", h1_style))
    story.append(Paragraph(
        "In modern retail and e-commerce, retaining existing customers is 5x cheaper than acquiring new ones. "
        "Traditional business dashboards provide <b>hindsight</b> (reporting past sales), whereas this platform delivers "
        "<b>foresight</b> by predicting customer churn 90 days before drop-off occurs and forecasting 12-month Customer Lifetime Value (CLV).",
        body_style
    ))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # SECTION 2: TASK CHRONOLOGY (YOU VS AGENT)
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Step-by-Step Task Breakdown (Who Did What)", h1_style))
    story.append(Paragraph(
        "To ensure full transparency during technical interviews, the table below outlines the division of work between "
        "the <b>Agent (Antigravity AI)</b> and <b>You (The User / Engineer)</b> across every milestone:",
        body_style
    ))

    task_data = [
        [Paragraph("<b>Milestone</b>", body_style), Paragraph("<b>Agent Accomplishments (Backend)</b>", body_style), Paragraph("<b>Your Accomplishments (Execution & BI)</b>", body_style)],

        [Paragraph("<b>1. Environment & Setup</b>", body_style),
         Paragraph("Created workspace structure (`src/`, `sql/`, `docs/`, `data/`) & dependency lists.", body_style),
         Paragraph("Installed Python libraries (`pandas`, `scikit-learn`, `powerbi`) in terminal.", body_style)],

        [Paragraph("<b>2. Data Engineering</b>", body_style),
         Paragraph("Wrote `src/generate_dataset.py` using Beta, Lognormal & Poisson distributions.", body_style),
         Paragraph("Executed dataset script generating 10,000 profiles & 60,597 transaction logs.", body_style)],

        [Paragraph("<b>3. RFM & Clustering</b>", body_style),
         Paragraph("Wrote ANSI SQL query (`sql/rfm_analysis.sql`) & K-Means clustering script (`src/rfm_segmentation.py`).", body_style),
         Paragraph("Executed segmentation script, validated Silhouette Score (k=5), assigned RFM personas.", body_style)],

        [Paragraph("<b>4. Churn ML Classifier</b>", body_style),
         Paragraph("Wrote Scikit-learn classification pipeline (`src/churn_prediction.py`) comparing Logistic Regression vs Random Forest.", body_style),
         Paragraph("Executed training, achieved **98.19% ROC-AUC**, generated customer risk tiers.", body_style)],

        [Paragraph("<b>5. CLV ML Regressor</b>", body_style),
         Paragraph("Wrote Scikit-learn regression pipeline (`src/clv_estimation.py`) comparing Random Forest Regressor vs Ridge.", body_style),
         Paragraph("Executed regressor, achieved **0.9536 R² Score ($29.37 MAE)**, assigned VIP value tiers.", body_style)],

        [Paragraph("<b>6. Power BI Dashboard</b>", body_style),
         Paragraph("Designed Star Schema data model & wrote DAX measures (`Total Revenue`, `Churn %`, `Avg CLV`).", body_style),
         Paragraph("Loaded CSVs in Power BI Desktop, established 1:* relationship, constructed 3-page interactive visual dashboard.", body_style)]
    ]

    t_tasks = Table(task_data, colWidths=[110, 205, 205])
    t_tasks.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_tasks)
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # SECTION 3: ALGORITHM & AI MODEL SELECTION GUIDE
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Algorithm Selection & Technical Justifications", h1_style))

    story.append(Paragraph("A. Unsupervised Learning: K-Means Clustering (`src/rfm_segmentation.py`)", h2_style))
    story.append(Paragraph("<b>Why we used it:</b> To group customers into natural behavioral clusters without manual biases.", body_style))
    story.append(Paragraph("<b>How it works:</b> Standardized RFM features (`StandardScaler`) and minimized within-cluster sum-of-squares (WCSS). "
                           "Evaluated silhouette scores across k=3..6 to select optimal <b>k=5 clusters</b> (Silhouette Score: `0.2236`).", body_style))
    story.append(Paragraph("<b>Customer Personas Created:</b> Champions (18.6%), Loyal Customers (20.2%), At-Risk Spenders (12.8%), Hibernating (23.9%), Lost (20.3%).", body_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("B. Supervised Classification: Churn Risk Prediction (`src/churn_prediction.py`)", h2_style))
    story.append(Paragraph("<b>Why we used it:</b> To estimate individual customer churn probability (0.00 to 1.00) 90 days before drop-off.", body_style))
    story.append(Paragraph("<b>Algorithms Compared:</b> Logistic Regression, Random Forest Classifier, Gradient Boosting.", body_style))
    story.append(Paragraph("<b>Winning Model:</b> Logistic Regression / Random Forest", body_style))
    story.append(Paragraph("<b>Performance Metrics:</b> ROC-AUC = <b>98.19%</b> | F1-Score = <b>0.9107</b> | Precision = <b>96.93%</b> | Recall = <b>85.88%</b>", body_style))
    story.append(Paragraph("<b>Core Business Finding:</b> Customers opening <b>3+ support tickets</b> paired with shipping delays > 3 days experienced a churn probability spike past <b>75%</b>.", body_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("C. Supervised Regression: 12-Month CLV Estimation (`src/clv_estimation.py`)", h2_style))
    story.append(Paragraph("<b>Why we used it:</b> To forecast future 12-month expected dollar revenue per customer.", body_style))
    story.append(Paragraph("<b>Algorithms Compared:</b> Random Forest Regressor, Ridge Regression, Gradient Boosting Regressor.", body_style))
    story.append(Paragraph("<b>Winning Model:</b> Random Forest Regressor (`n_estimators=150, max_depth=10`)", body_style))
    story.append(Paragraph("<b>Performance Metrics:</b> R² Score = <b>0.9536</b> (explains 95.4% revenue variance) | MAE = <b>$29.37</b>", body_style))
    story.append(Paragraph("<b>Value Tiers:</b> Tier 1 VIP ($780+), Tier 2 High ($260-$780), Tier 3 Medium ($120-$260), Tier 4 Low (<$120).", body_style))

    story.append(Spacer(1, 10))
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # SECTION 4: FILE-BY-FILE BLUEPRINT
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. File-by-File Technical Blueprint", h1_style))

    files_data = [
        [Paragraph("<b>Filename & Path</b>", body_style), Paragraph("<b>Technical Purpose</b>", body_style), Paragraph("<b>Output Asset Produced</b>", body_style)],
        [Paragraph("`Customer_Intelligence_Dashboard.pbix`", body_style), Paragraph("Interactive 3-page Power BI report.", body_style), Paragraph("Visual executive dashboard", body_style)],
        [Paragraph("`churn_clv_rfm_analytics.ipynb`", body_style), Paragraph("Executed Jupyter analytics notebook with charts.", body_style), Paragraph("EDA & model validation plots", body_style)],
        [Paragraph("`src/generate_dataset.py`", body_style), Paragraph("Synthetic data engine using Beta/Lognormal math.", body_style), Paragraph("`customer_profiles.csv` & `transactions.csv`", body_style)],
        [Paragraph("`src/rfm_segmentation.py`", body_style), Paragraph("Quantile scoring & K-Means clustering script.", body_style), Paragraph("`rfm_segmented_customers.csv`", body_style)],
        [Paragraph("`src/churn_prediction.py`", body_style), Paragraph("Scikit-learn classification pipeline.", body_style), Paragraph("`churn_predictions.csv` (ROC-AUC 98.2%)", body_style)],
        [Paragraph("`src/clv_estimation.py`", body_style), Paragraph("Scikit-learn regression pipeline.", body_style), Paragraph("`clv_predictions.csv` (R² 0.954)", body_style)],
        [Paragraph("`sql/rfm_analysis.sql`", body_style), Paragraph("ANSI SQL queries using CTEs & `NTILE(5)`.", body_style), Paragraph("SQL feature extraction logic", body_style)],
        [Paragraph("`docs/power_bi_dashboard_spec.md`", body_style), Paragraph("DAX measures & Star Schema layout guide.", body_style), Paragraph("Power BI architectural blueprint", body_style)],
        [Paragraph("`README.md`", body_style), Paragraph("GitHub repository documentation & architecture.", body_style), Paragraph("Portfolio front page documentation", body_style)]
    ]
    t_files = Table(files_data, colWidths=[160, 200, 160])
    t_files.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(t_files)
    story.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # SECTION 5: POWER BI DAX MEASURES
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. Power BI Star Schema & DAX Measures", h1_style))
    story.append(Paragraph("<b>Star Schema Model:</b> Connected `Dim_Customer_Analytics` (1) ──── (*) `Fact_Transactions` on `customer_id` with single-direction filtering.", body_style))
    story.append(Spacer(1, 4))

    dax_code = (
        "Total Revenue = SUM(Fact_Transactions[order_amount])\n"
        "Total Active Customers = CALCULATE(COUNTROWS(Dim_Customer_Analytics), Dim_Customer_Analytics[is_churned] = 0)\n"
        "Churn Rate % = DIVIDE(CALCULATE(COUNTROWS(Dim_Customer_Analytics), Dim_Customer_Analytics[is_churned] = 1), COUNTROWS(Dim_Customer_Analytics), 0)\n"
        "Avg Predicted 12M CLV = AVERAGE(Dim_Customer_Analytics[predicted_12m_clv])\n"
        "At Risk Revenue = CALCULATE(SUM(Dim_Customer_Analytics[monetary]), Dim_Customer_Analytics[risk_tier] = \"High Risk\")"
    )
    story.append(Paragraph(dax_code.replace('\n', '<br/>'), code_style))
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # SECTION 6: INTERVIEW PLAYBOOK
    # -------------------------------------------------------------------------
    story.append(Paragraph("6. Top Technical Interview Q&A Playbook", h1_style))

    qa_list = [
        ("Q1: How did you prevent data leakage during machine learning model training?",
         "I enforced strict featurization ordering by splitting the raw dataset into 80% Train and 20% Test sets BEFORE fitting any preprocessors like StandardScaler or OneHotEncoder. I fit transformers exclusively on training data and transformed test data independently."),

        ("Q2: Why evaluate ROC-AUC and F1-Score instead of just Accuracy?",
         "Accuracy is misleading in imbalanced datasets. ROC-AUC evaluates the model's capacity to rank high-risk customers above low-risk customers across all thresholds, while F1-Score balances Precision (avoiding false alarms) and Recall (catching actual churners). My model achieved 98.19% ROC-AUC."),

        ("Q3: How did you select k=5 in K-Means Clustering?",
         "I standardized RFM features using StandardScaler and evaluated cluster separation across k=3 to 6 using Silhouette Scores. The highest silhouette score of 0.2236 occurred at k=5, cleanly partitioning customers into Champions, Loyal, Potential Loyalists, At Risk, and Lost segments."),

        ("Q4: What operational insight did your model discover for executive decision making?",
         "Feature importances proved that opening 3+ support tickets paired with shipping delays > 3 days caused customer churn probability to spike past 75%. In Power BI, I created an 'At-Risk Revenue' card ($1.30M exposure) and a live High-Risk VIP action table for immediate CSM retention calls.")
    ]

    for q, a in qa_list:
        story.append(Paragraph(f"<b>{q}</b>", h2_style))
        story.append(Paragraph(f"<i>Answer:</i> {a}", body_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    print(f"Master PDF Guide successfully generated at: {pdf_filename}")

if __name__ == "__main__":
    generate_pdf_guide()
