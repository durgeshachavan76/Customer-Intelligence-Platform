import os
from typing import List, Optional
import pandas as pd
import numpy as np
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title='Customer Intelligence Platform — Live Inference API',
    description='Production REST API for real-time Churn Prediction, Customer Lifetime Value (CLV) Estimation, and RFM Segmentation.',
    version='1.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Load Models at Startup
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == 'src' else script_dir
models_dir = os.path.join(project_root, 'models')
data_dir = os.path.join(project_root, 'data')

churn_model_path = os.path.join(models_dir, 'churn_pipeline.joblib')
clv_model_path = os.path.join(models_dir, 'clv_pipeline.joblib')

if os.path.exists(churn_model_path):
    churn_model = joblib.load(churn_model_path)
else:
    churn_model = None

if os.path.exists(clv_model_path):
    clv_model = joblib.load(clv_model_path)
else:
    clv_model = None

# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------
class CustomerInput(BaseModel):
    customer_id: str = Field(default='CUST-10001', example='CUST-10001')
    recency_days: int = Field(default=45, ge=0, example=45)
    frequency: int = Field(default=6, ge=1, example=6)
    monetary: float = Field(default=480.50, ge=0.0, example=480.50)
    avg_order_value: float = Field(default=80.08, ge=0.0, example=80.08)
    total_items_purchased: int = Field(default=14, ge=1, example=14)
    avg_shipping_delay: float = Field(default=1.2, ge=0.0, example=1.2)
    total_returns: int = Field(default=0, ge=0, example=0)
    avg_discount_rate: float = Field(default=0.05, ge=0.0, le=1.0, example=0.05)
    tenure_days: int = Field(default=320, ge=1, example=320)
    support_tickets_opened: int = Field(default=1, ge=0, example=1)
    email_open_rate: float = Field(default=0.65, ge=0.0, le=1.0, example=0.65)
    app_installed: int = Field(default=1, ge=0, le=1, example=1)
    acquisition_channel: str = Field(default='Organic Search', example='Organic Search')
    country: str = Field(default='USA', example='USA')
    preferred_category: str = Field(default='Electronics', example='Electronics')

class ChurnResponse(BaseModel):
    customer_id: str
    churn_probability: float
    is_churn_predicted: bool
    risk_tier: str
    primary_risk_driver: str

class CLVResponse(BaseModel):
    customer_id: str
    predicted_12m_clv: float
    clv_tier: str
    confidence_interval_95: List[float]

class FullIntelligenceProfile(BaseModel):
    customer_id: str
    rfm_segment: str
    churn_probability: float
    risk_tier: str
    predicted_12m_clv: float
    clv_tier: str
    retention_recommendation: str

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------
@app.get('/', tags=['System Health'])
def root():
    return {
        'service': 'Customer Intelligence Platform ML Inference API',
        'status': 'Online',
        'version': '1.0.0',
        'docs_url': '/docs'
    }

@app.get('/health', tags=['System Health'])
def health_check():
    return {
        'status': 'healthy',
        'models_loaded': {
            'churn_model': churn_model is not None,
            'clv_model': clv_model is not None
        }
    }

@app.post('/api/v1/predict/churn', response_model=ChurnResponse, tags=['Predictions'])
def predict_churn(customer: CustomerInput):
    if churn_model is None:
        raise HTTPException(status_code=503, detail='Churn model not loaded. Train models first.')

    # Calculate synthetic RFM scores
    r_score = 5 if customer.recency_days <= 30 else (4 if customer.recency_days <= 60 else (3 if customer.recency_days <= 90 else (2 if customer.recency_days <= 120 else 1)))
    f_score = 5 if customer.frequency >= 8 else (4 if customer.frequency >= 6 else (3 if customer.frequency >= 4 else (2 if customer.frequency >= 2 else 1)))
    m_score = 5 if customer.monetary >= 600 else (4 if customer.monetary >= 400 else (3 if customer.monetary >= 250 else (2 if customer.monetary >= 100 else 1)))
    rfm_total = r_score + f_score + m_score

    df_row = pd.DataFrame([{
        'R_Score': r_score,
        'F_Score': f_score,
        'M_Score': m_score,
        'rfm_total_score': rfm_total,
        'monetary': customer.monetary,
        'avg_order_value': customer.avg_order_value,
        'total_items_purchased': customer.total_items_purchased,
        'avg_shipping_delay': customer.avg_shipping_delay,
        'total_returns': customer.total_returns,
        'avg_discount_rate': customer.avg_discount_rate,
        'tenure_days': customer.tenure_days,
        'support_tickets_opened': customer.support_tickets_opened,
        'email_open_rate': customer.email_open_rate,
        'app_installed': customer.app_installed,
        'acquisition_channel': customer.acquisition_channel,
        'country': customer.country,
        'preferred_category': customer.preferred_category
    }])

    prob = float(churn_model.predict_proba(df_row)[0, 1])
    is_churn = bool(prob >= 0.50)

    if prob >= 0.60:
        tier = 'High Risk'
    elif prob >= 0.30:
        tier = 'Medium Risk'
    else:
        tier = 'Low Risk'

    driver = 'Support Ticket Friction' if customer.support_tickets_opened >= 3 else ('Inactivity Decay' if customer.recency_days > 90 else 'Low Email Engagement')

    return ChurnResponse(
        customer_id=customer.customer_id,
        churn_probability=round(prob, 4),
        is_churn_predicted=is_churn,
        risk_tier=tier,
        primary_risk_driver=driver
    )

@app.post('/api/v1/predict/clv', response_model=CLVResponse, tags=['Predictions'])
def predict_clv(customer: CustomerInput):
    if clv_model is None:
        raise HTTPException(status_code=503, detail='CLV model not loaded. Train models first.')

    df_row = pd.DataFrame([{
        'recency_days': customer.recency_days,
        'frequency': customer.frequency,
        'monetary': customer.monetary,
        'avg_order_value': customer.avg_order_value,
        'total_items_purchased': customer.total_items_purchased,
        'avg_shipping_delay': customer.avg_shipping_delay,
        'total_returns': customer.total_returns,
        'avg_discount_rate': customer.avg_discount_rate,
        'tenure_days': customer.tenure_days,
        'support_tickets_opened': customer.support_tickets_opened,
        'email_open_rate': customer.email_open_rate,
        'app_installed': customer.app_installed,
        'acquisition_channel': customer.acquisition_channel,
        'country': customer.country,
        'preferred_category': customer.preferred_category
    }])

    pred_clv = float(clv_model.predict(df_row)[0])
    pred_clv = max(25.0, round(pred_clv, 2))

    if pred_clv >= 700:
        tier = 'Tier 1 (VIP CLV)'
    elif pred_clv >= 250:
        tier = 'Tier 2 (High CLV)'
    elif pred_clv >= 120:
        tier = 'Tier 3 (Medium CLV)'
    else:
        tier = 'Tier 4 (Low CLV)'

    ci_low = round(pred_clv * 0.90, 2)
    ci_high = round(pred_clv * 1.10, 2)

    return CLVResponse(
        customer_id=customer.customer_id,
        predicted_12m_clv=pred_clv,
        clv_tier=tier,
        confidence_interval_95=[ci_low, ci_high]
    )

@app.post('/api/v1/predict/profile', response_model=FullIntelligenceProfile, tags=['Customer Intelligence'])
def generate_full_profile(customer: CustomerInput):
    churn_res = predict_churn(customer)
    clv_res = predict_clv(customer)

    # RFM Segment Rule
    if customer.recency_days <= 45 and customer.frequency >= 5 and customer.monetary >= 400:
        seg = 'Champions'
    elif customer.recency_days <= 75 and customer.frequency >= 3:
        seg = 'Loyal Customers'
    elif customer.recency_days > 120 and customer.monetary >= 350:
        seg = 'At Risk Spenders'
    elif customer.recency_days > 120:
        seg = 'Lost Customers'
    else:
        seg = 'Potential Loyalists'

    if churn_res.risk_tier == 'High Risk' and seg in ['Champions', 'Loyal Customers', 'At Risk Spenders']:
        rec = 'URGENT: Initiate White-Glove CSM Outreach +  Loyalty Voucher within 24 hours.'
    elif churn_res.risk_tier == 'Medium Risk':
        rec = 'Trigger personalized category email discount based on preferred_category.'
    elif clv_res.clv_tier == 'Tier 1 (VIP CLV)':
        rec = 'Enroll in VIP Tier 1 Exclusive Early-Access Beta Club.'
    else:
        rec = 'Maintain standard automated monthly newsletter nurturing.'

    return FullIntelligenceProfile(
        customer_id=customer.customer_id,
        rfm_segment=seg,
        churn_probability=churn_res.churn_probability,
        risk_tier=churn_res.risk_tier,
        predicted_12m_clv=clv_res.predicted_12m_clv,
        clv_tier=clv_res.clv_tier,
        retention_recommendation=rec
    )
