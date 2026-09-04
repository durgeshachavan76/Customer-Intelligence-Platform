import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def run_rfm_segmentation():
    """
    Performs RFM Segmentation & K-Means Clustering on Customer Data.
    """
    print("Starting RFM Customer Segmentation & Behavioral Analysis...")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == 'src' else script_dir
    data_dir = os.path.join(project_root, 'data')

    profiles_path = os.path.join(data_dir, 'customer_profiles.csv')
    trans_path = os.path.join(data_dir, 'customer_transactions.csv')

    if not os.path.exists(profiles_path) or not os.path.exists(trans_path):
        raise FileNotFoundError("Raw data files missing! Run generate_dataset.py first.")

    profiles_df = pd.read_csv(profiles_path)
    trans_df = pd.read_csv(trans_path)

    snapshot_date = pd.to_datetime('2026-01-01')
    trans_df['transaction_date'] = pd.to_datetime(trans_df['transaction_date'])
    profiles_df['signup_date'] = pd.to_datetime(profiles_df['signup_date'])

    # 1. Aggregate Transactions per Customer
    rfm_agg = trans_df.groupby('customer_id').agg({
        'transaction_date': lambda x: (snapshot_date - x.max()).days, # Recency
        'transaction_id': 'count',                                   # Frequency
        'order_amount': ['sum', 'mean'],                             # Monetary & AOV
        'items_count': 'sum',
        'shipping_delay_days': 'mean',
        'is_returned': 'sum',
        'discount_applied': 'mean'
    })

    rfm_agg.columns = [
        'recency_days', 'frequency', 'monetary', 'avg_order_value',
        'total_items_purchased', 'avg_shipping_delay', 'total_returns', 'avg_discount_rate'
    ]
    rfm_agg = rfm_agg.reset_index()

    df = pd.merge(rfm_agg, profiles_df, on='customer_id', how='inner')
    df['tenure_days'] = (snapshot_date - df['signup_date']).dt.days

    # 2. RFM Quantile Scoring (1-5)
    df['R_Score'] = pd.qcut(df['recency_days'], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    df['F_Score'] = pd.qcut(df['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    df['M_Score'] = pd.qcut(df['monetary'], q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    df['rfm_total_score'] = df['R_Score'] + df['F_Score'] + df['M_Score']

    # 3. Rule-Based Segment Mapping
    def map_rfm_segment(row):
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3 and m >= 3:
            return 'Loyal Customers'
        elif r >= 3 and f < 3 and m >= 3:
            return 'Potential Loyalists'
        elif r < 3 and f >= 3 and m >= 3:
            return 'At Risk Spenders'
        elif r <= 2 and f <= 2 and m <= 2:
            return 'Lost Customers'
        else:
            return 'Hibernating / Needing Attention'

    df['rfm_segment'] = df.apply(map_rfm_segment, axis=1)

    # 4. Machine Learning: K-Means Clustering
    rfm_features = ['recency_days', 'frequency', 'monetary', 'tenure_days', 'support_tickets_opened']
    scaler = StandardScaler()
    scaled_rfm = scaler.fit_transform(df[rfm_features])

    best_k = 5
    sample_scaled = scaled_rfm[:2000]
    best_score = -1
    for k in range(3, 6):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=3)
        labels = kmeans.fit_predict(sample_scaled)
        score = silhouette_score(sample_scaled, labels)
        if score > best_score:
            best_score = score
            best_k = k

    print(f"K-Means Optimal Clusters (k): {best_k} (Silhouette Score: {best_score:.4f})")

    final_kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=5)
    df['kmeans_cluster'] = final_kmeans.fit_predict(scaled_rfm)

    # Define Target Variable for Churn: Recency > 120 days
    df['is_churned'] = (df['recency_days'] > 120).astype(int)

    output_path = os.path.join('data', 'rfm_segmented_customers.csv')
    df.to_csv(output_path, index=False)

    print("\n--- RFM Customer Segmentation Summary ---")
    print(df['rfm_segment'].value_counts())
    print(f"\nOverall Churn Rate: {df['is_churned'].mean()*100:.2f}%")
    print(f"Segmented customer dataset saved to: {output_path}")

    return df

if __name__ == "__main__":
    run_rfm_segmentation()
