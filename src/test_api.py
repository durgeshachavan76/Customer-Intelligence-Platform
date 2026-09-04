import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def run_api_tests():
    print('Starting FastAPI TestClient verification...')

    # 1. Health Check
    res = client.get('/health')
    assert res.status_code == 200
    print(' [PASS] GET /health:', res.json())

    # 2. Churn Prediction Endpoint (Low Risk Champion)
    payload_champ = {
        'customer_id': 'CUST-TEST-001',
        'recency_days': 15,
        'frequency': 8,
        'monetary': 750.0,
        'avg_order_value': 93.75,
        'total_items_purchased': 20,
        'avg_shipping_delay': 0.5,
        'total_returns': 0,
        'avg_discount_rate': 0.05,
        'tenure_days': 400,
        'support_tickets_opened': 0,
        'email_open_rate': 0.85,
        'app_installed': 1,
        'acquisition_channel': 'Organic Search',
        'country': 'USA',
        'preferred_category': 'Electronics'
    }
    res_churn = client.post('/api/v1/predict/churn', json=payload_champ)
    assert res_churn.status_code == 200
    print(' [PASS] POST /api/v1/predict/churn (Champion):', res_churn.json())

    # 3. Churn Prediction Endpoint (High Risk Customer with 4 support tickets)
    payload_risk = {
        'customer_id': 'CUST-TEST-002',
        'recency_days': 160,
        'frequency': 2,
        'monetary': 120.0,
        'avg_order_value': 60.0,
        'total_items_purchased': 3,
        'avg_shipping_delay': 4.5,
        'total_returns': 2,
        'avg_discount_rate': 0.20,
        'tenure_days': 200,
        'support_tickets_opened': 4,
        'email_open_rate': 0.15,
        'app_installed': 0,
        'acquisition_channel': 'Paid Ads',
        'country': 'USA',
        'preferred_category': 'Apparel'
    }
    res_churn_risk = client.post('/api/v1/predict/churn', json=payload_risk)
    assert res_churn_risk.status_code == 200
    print(' [PASS] POST /api/v1/predict/churn (High Risk):', res_churn_risk.json())

    # 4. CLV Prediction Endpoint
    res_clv = client.post('/api/v1/predict/clv', json=payload_champ)
    assert res_clv.status_code == 200
    print(' [PASS] POST /api/v1/predict/clv:', res_clv.json())

    # 5. Full Intelligence Profile Endpoint
    res_profile = client.post('/api/v1/predict/profile', json=payload_champ)
    assert res_profile.status_code == 200
    print(' [PASS] POST /api/v1/predict/profile:', res_profile.json())

    print("\nAll 5 API endpoint tests passed successfully!")

if __name__ == '__main__':
    run_api_tests()
