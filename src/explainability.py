import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression

def generate_explainability_and_cohorts():
    print('Starting Explainable AI & Cohort Retention Processing...')

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == 'src' else script_dir
    data_dir = os.path.join(project_root, 'data')
    models_dir = os.path.join(project_root, 'models')
    os.makedirs(models_dir, exist_ok=True)

    # 1. Load Data
    profiles_df = pd.read_csv(os.path.join(data_dir, 'customer_profiles.csv'))
    trans_df = pd.read_csv(os.path.join(data_dir, 'customer_transactions.csv'))
    clv_df = pd.read_csv(os.path.join(data_dir, 'clv_predictions.csv'))

    # 2. Train & Serialize Churn Model Pipeline
    numeric_features_churn = [
        'R_Score', 'F_Score', 'M_Score', 'rfm_total_score', 'monetary',
        'avg_order_value', 'total_items_purchased', 'avg_shipping_delay',
        'total_returns', 'avg_discount_rate', 'tenure_days',
        'support_tickets_opened', 'email_open_rate', 'app_installed'
    ]
    categorical_features = ['acquisition_channel', 'country', 'preferred_category']

    X_churn = clv_df[numeric_features_churn + categorical_features]
    y_churn = clv_df['is_churned']

    preprocessor_churn = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features_churn),
            ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_features)
        ]
    )

    rf_churn = RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42)
    churn_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor_churn),
        ('classifier', rf_churn)
    ])
    churn_pipeline.fit(X_churn, y_churn)

    churn_model_path = os.path.join(models_dir, 'churn_pipeline.joblib')
    joblib.dump(churn_pipeline, churn_model_path)
    print(f'Churn model serialized to: {churn_model_path}')

    # 3. Train & Serialize CLV Model Pipeline
    numeric_features_clv = [
        'recency_days', 'frequency', 'monetary', 'avg_order_value', 'total_items_purchased',
        'avg_shipping_delay', 'total_returns', 'avg_discount_rate', 'tenure_days',
        'support_tickets_opened', 'email_open_rate', 'app_installed'
    ]
    X_clv = clv_df[numeric_features_clv + categorical_features]
    y_clv = clv_df['predicted_12m_clv']

    preprocessor_clv = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features_clv),
            ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_features)
        ]
    )

    rf_clv = RandomForestRegressor(n_estimators=150, max_depth=10, random_state=42)
    clv_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor_clv),
        ('regressor', rf_clv)
    ])
    clv_pipeline.fit(X_clv, y_clv)

    clv_model_path = os.path.join(models_dir, 'clv_pipeline.joblib')
    joblib.dump(clv_pipeline, clv_model_path)
    print(f'CLV model serialized to: {clv_model_path}')

    # 4. Feature Importance Extraction (XAI Churn Drivers)
    cat_encoder = churn_pipeline.named_steps['preprocessor'].named_transformers_['cat']
    encoded_cat_names = list(cat_encoder.get_feature_names_out(categorical_features))
    all_feature_names = numeric_features_churn + encoded_cat_names

    importances = rf_churn.feature_importances_

    driver_df = pd.DataFrame({
        'feature_name': all_feature_names,
        'importance_weight': importances
    }).sort_values(by='importance_weight', ascending=False).reset_index(drop=True)

    driver_df['relative_impact_pct'] = np.round((driver_df['importance_weight'] / driver_df['importance_weight'].sum()) * 100, 2)

    # Map friendly business explanations
    descriptions = {
        'R_Score': 'Recent inactivity and lapse since last order',
        'support_tickets_opened': 'Customer service friction and unresolved complaints',
        'email_open_rate': 'Brand engagement and marketing responsiveness',
        'monetary': 'Historical spend volume and economic attachment',
        'avg_shipping_delay': 'Logistics bottlenecks and delivery friction',
        'rfm_total_score': 'Composite RFM customer loyalty health score',
        'total_returns': 'Product dissatisfaction and return frequency',
        'F_Score': 'Purchase frequency and re-order habits',
        'tenure_days': 'Customer lifetime age and brand familiarity',
        'avg_order_value': 'Average basket size per order',
        'M_Score': 'Monetary spend quintile tier',
        'app_installed': 'Mobile ecosystem adoption and accessibility',
        'total_items_purchased': 'Cumulative physical items ordered',
        'avg_discount_rate': 'Price sensitivity and promo dependency'
    }
    driver_df['business_description'] = driver_df['feature_name'].map(descriptions).fillna('Channel or Demographic Segment Factor')
    driver_df['driver_type'] = driver_df['feature_name'].apply(
        lambda x: 'Operational Friction' if x in ['support_tickets_opened', 'avg_shipping_delay', 'total_returns']
        else ('Customer Engagement' if x in ['email_open_rate', 'app_installed', 'R_Score']
        else 'Financial & Monetary')
    )

    driver_path = os.path.join(data_dir, 'churn_driver_analysis.csv')
    driver_df.to_csv(driver_path, index=False)
    print(f'Churn Drivers (XAI) saved to: {driver_path}')

    # 5. Cohort Retention Analysis
    trans_df['transaction_date'] = pd.to_datetime(trans_df['transaction_date'])
    profiles_df['signup_date'] = pd.to_datetime(profiles_df['signup_date'])

    # Merge transactions with signup date
    merged_trans = pd.merge(trans_df, profiles_df[['customer_id', 'signup_date', 'acquisition_channel']], on='customer_id')

    merged_trans['signup_quarter'] = merged_trans['signup_date'].dt.to_period('Q').astype(str)
    merged_trans['signup_year_month'] = merged_trans['signup_date'].dt.to_period('M').astype(str)

    # Calculate months elapsed between transaction and signup
    merged_trans['months_since_signup'] = (
        (merged_trans['transaction_date'].dt.year - merged_trans['signup_date'].dt.year) * 12 +
        (merged_trans['transaction_date'].dt.month - merged_trans['signup_date'].dt.month)
    )

    # Cohort Size by Quarter
    cohort_sizes = profiles_df.copy()
    cohort_sizes['signup_quarter'] = cohort_sizes['signup_date'].dt.to_period('Q').astype(str)
    cohort_total_custs = cohort_sizes.groupby('signup_quarter')['customer_id'].nunique()

    # Monthly Active Customers per Cohort
    cohort_activity = merged_trans.groupby(['signup_quarter', 'months_since_signup'])['customer_id'].nunique().reset_index()
    cohort_activity = cohort_activity[cohort_activity['months_since_signup'].between(0, 12)]

    # Pivot to Matrix
    cohort_pivot = cohort_activity.pivot(index='signup_quarter', columns='months_since_signup', values='customer_id').fillna(0)

    # Calculate Retention Rate %
    cohort_retention = cohort_pivot.divide(cohort_total_custs, axis=0) * 100
    cohort_retention = cohort_retention.round(1)

    cohort_matrix_df = cohort_retention.reset_index()
    cohort_matrix_df['Cohort_Size'] = cohort_matrix_df['signup_quarter'].map(cohort_total_custs)

    # Rename columns for Power BI
    rename_cols = {i: f'Month_{i}' for i in range(13)}
    cohort_matrix_df = cohort_matrix_df.rename(columns=rename_cols)

    # Melt for Power BI Heatmap Visual
    cohort_melted = pd.melt(
        cohort_matrix_df,
        id_vars=['signup_quarter', 'Cohort_Size'],
        value_vars=[col for col in cohort_matrix_df.columns if col.startswith('Month_')],
        var_name='Retention_Month',
        value_name='Retention_Rate_Pct'
    )

    cohort_path = os.path.join(data_dir, 'cohort_retention_matrix.csv')
    cohort_melted.to_csv(cohort_path, index=False)
    print(f'Cohort Retention Matrix saved to: {cohort_path}')

    # Also save un-melted wide table
    cohort_matrix_df.to_csv(os.path.join(data_dir, 'cohort_retention_summary.csv'), index=False)

    print('All XAI and Cohort assets successfully generated!')

if __name__ == '__main__':
    generate_explainability_and_cohorts()
