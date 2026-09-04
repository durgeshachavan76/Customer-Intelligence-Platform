import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def train_clv_estimation_models():
    """
    Trains and evaluates Scikit-learn Regression Models to estimate Customer Lifetime Value (CLV).
    Follows ML Best Practices for Regression:
    - Train / Test split BEFORE preprocessing.
    - Multiple regression model comparison (Ridge, Random Forest Regressor, Gradient Boosting).
    - Evaluation via R² Score, RMSE, and MAE.
    """
    print("\n========================================================")
    print("      BUILDING CUSTOMER LIFETIME VALUE (CLV) PIPELINE  ")
    print("========================================================\n")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == 'src' else script_dir
    data_dir = os.path.join(project_root, 'data')

    data_path = os.path.join(data_dir, 'churn_predictions.csv')
    if not os.path.exists(data_path):
        # Fallback to rfm_segmented_customers if churn predictions haven't run yet
        data_path = os.path.join(data_dir, 'rfm_segmented_customers.csv')

    df = pd.read_csv(data_path)

    # 1. Target Feature Engineering: Synthetic 12-Month Future CLV
    # Formula based on historical monetary spend, frequency, tenure, email engagement, and churn risk
    np.random.seed(42)
    annualized_monetary = (df['monetary'] / np.maximum(df['tenure_days'], 30)) * 365
    future_multiplier = 0.85 + 0.40 * df['email_open_rate'] - 0.50 * (df['recency_days'] > 120).astype(int) + np.random.normal(0, 0.1, len(df))
    future_multiplier = np.clip(future_multiplier, 0.10, 2.50)

    df['target_12m_clv'] = np.round(annualized_monetary * future_multiplier, 2)
    df['target_12m_clv'] = np.maximum(df['target_12m_clv'], 25.0)

    # 2. Select Features for Regression
    numeric_features = [
        'recency_days', 'frequency', 'monetary', 'avg_order_value', 'total_items_purchased',
        'avg_shipping_delay', 'total_returns', 'avg_discount_rate', 'tenure_days',
        'support_tickets_opened', 'email_open_rate', 'app_installed'
    ]
    categorical_features = ['acquisition_channel', 'country', 'preferred_category']

    X = df[numeric_features + categorical_features]
    y = df['target_12m_clv']

    # 3. Train-Test Split (80% Train, 20% Test) BEFORE fitting preprocessors
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    print(f"Data Split: Train Set = {len(X_train)} rows | Test Set = {len(X_test)} rows")
    print(f"Mean 12M Target CLV (Train): ${y_train.mean():,.2f}")
    print(f"Mean 12M Target CLV (Test):  ${y_test.mean():,.2f}\n")

    # 4. Preprocessing Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_features)
        ]
    )

    # 5. Candidate Models
    models = {
        'Ridge Regression': Ridge(alpha=1.0, random_state=42),
        'Random Forest Regressor': RandomForestRegressor(n_estimators=150, max_depth=10, random_state=42),
        'Gradient Boosting Regressor': GradientBoostingRegressor(n_estimators=150, learning_rate=0.08, max_depth=5, random_state=42)
    }

    results = {}
    best_model_name = None
    best_r2 = -1.0
    best_pipeline = None

    # 6. Fit & Evaluate Models
    for name, model in models.items():
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', model)
        ])

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)

        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)

        results[name] = {
            'R2_Score': r2,
            'RMSE': rmse,
            'MAE': mae,
            'Pipeline': pipeline
        }

        print(f"--- Model: {name} ---")
        print(f"  R2 Score: {r2:.4f}")
        print(f"  RMSE:     ${rmse:,.2f}")
        print(f"  MAE:      ${mae:,.2f}\n")

        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
            best_pipeline = pipeline

    print(f"[BEST MODEL] Best Regressor Model: {best_model_name} with R2 = {best_r2:.4f}")

    # 7. Predict CLV for All Customers
    df['predicted_12m_clv'] = np.round(best_pipeline.predict(X), 2)
    df['clv_tier'] = pd.qcut(
        df['predicted_12m_clv'],
        q=4,
        labels=['Tier 4 (Low CLV)', 'Tier 3 (Medium CLV)', 'Tier 2 (High CLV)', 'Tier 1 (VIP CLV)']
    )

    output_path = os.path.join('data', 'clv_predictions.csv')
    df.to_csv(output_path, index=False)
    print(f"\nFull customer CLV predictions saved to: {output_path}")

    return results, best_model_name, best_r2, results[best_model_name]['RMSE']

if __name__ == "__main__":
    train_clv_estimation_models()
