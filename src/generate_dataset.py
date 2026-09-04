import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_customer_intelligence_data(num_customers=10000, seed=42):
    """
    Generates a realistic E-Commerce Customer Intelligence dataset:
    - Customer Profiles (demographics, support history, engagement)
    - Transactions (60,000+ purchases over 24 months)
    """
    np.random.seed(seed)

    # Resolve project root and data folder path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == 'src' else script_dir
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)

    print(f"Generating data for {num_customers} customers...")

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range_days = (end_date - start_date).days

    # 1. Customer Profiles
    customer_ids = [f"CUST-{10000 + i}" for i in range(num_customers)]
    signup_dates = [start_date + timedelta(days=int(np.random.beta(2, 5) * date_range_days * 0.7)) for _ in range(num_customers)]
    channels = np.random.choice(['Organic Search', 'Paid Ads', 'Social Media', 'Email Campaign', 'Referral'], size=num_customers, p=[0.30, 0.25, 0.20, 0.15, 0.10])
    countries = np.random.choice(['USA', 'Canada', 'UK', 'Germany', 'Australia'], size=num_customers, p=[0.50, 0.15, 0.15, 0.10, 0.10])
    preferred_categories = np.random.choice(['Electronics', 'Apparel', 'Home & Kitchen', 'Beauty & Health', 'Sports'], size=num_customers)

    profiles_df = pd.DataFrame({
        'customer_id': customer_ids,
        'signup_date': [d.strftime('%Y-%m-%d') for d in signup_dates],
        'acquisition_channel': channels,
        'country': countries,
        'preferred_category': preferred_categories,
        'support_tickets_opened': np.random.poisson(lam=1.5, size=num_customers),
        'email_open_rate': np.round(np.random.beta(5, 2, size=num_customers), 2),
        'app_installed': np.random.choice([1, 0], size=num_customers, p=[0.65, 0.35])
    })

    # 2. Transactions Generation
    transactions = []
    trans_counter = 100000

    base_activity = np.random.gamma(shape=2.0, scale=3.0, size=num_customers)
    base_spend = np.random.lognormal(mean=4.2, sigma=0.6, size=num_customers)

    for i, cid in enumerate(customer_ids):
        c_signup = signup_dates[i]
        active_days = (end_date - c_signup).days
        if active_days <= 0:
            continue

        n_orders = max(1, int(np.random.poisson(base_activity[i])))

        churn_bias = 0.2 + 0.15 * (profiles_df.loc[i, 'support_tickets_opened'] > 3) - 0.1 * (profiles_df.loc[i, 'email_open_rate'] > 0.7)
        churn_bias = np.clip(churn_bias, 0.05, 0.85)
        is_churned = np.random.rand() < churn_bias

        if is_churned:
            max_offset = max(1, active_days - 180)
            order_days = np.sort(np.random.randint(0, max_offset, size=n_orders))
        else:
            order_days = np.sort(np.random.randint(0, active_days, size=n_orders))

        for day_offset in order_days:
            t_date = c_signup + timedelta(days=int(day_offset))
            if t_date > end_date:
                continue

            trans_counter += 1
            order_val = round(float(np.random.normal(loc=base_spend[i], scale=base_spend[i]*0.25)), 2)
            order_val = max(12.50, order_val)

            items_cnt = max(1, int(np.random.poisson(lam=order_val/35.0)))
            category = profiles_df.loc[i, 'preferred_category'] if np.random.rand() < 0.7 else np.random.choice(['Electronics', 'Apparel', 'Home & Kitchen', 'Beauty & Health', 'Sports'])
            discount = round(float(np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20], p=[0.40, 0.25, 0.20, 0.10, 0.05])), 2)
            payment = np.random.choice(['Credit Card', 'PayPal', 'Apple Pay', 'Debit Card'], p=[0.55, 0.25, 0.12, 0.08])
            ship_delay = int(np.random.choice([0, 1, 2, 3, 5, 7], p=[0.50, 0.25, 0.12, 0.08, 0.03, 0.02]))
            is_returned = 1 if (np.random.rand() < (0.05 + 0.03 * (ship_delay > 3))) else 0

            transactions.append({
                'transaction_id': f"TXN-{trans_counter}",
                'customer_id': cid,
                'transaction_date': t_date.strftime('%Y-%m-%d %H:%M:%S'),
                'order_amount': order_val,
                'items_count': items_cnt,
                'product_category': category,
                'discount_applied': discount,
                'payment_method': payment,
                'shipping_delay_days': ship_delay,
                'is_returned': is_returned
            })

    trans_df = pd.DataFrame(transactions)

    profiles_path = os.path.join('data', 'customer_profiles.csv')
    trans_path = os.path.join('data', 'customer_transactions.csv')

    profiles_df.to_csv(profiles_path, index=False)
    trans_df.to_csv(trans_path, index=False)

    print(f"Dataset successfully created!")
    print(f" - Profiles saved to: {profiles_path} ({len(profiles_df)} records)")
    print(f" - Transactions saved to: {trans_path} ({len(trans_df)} records)")
    return profiles_df, trans_df

if __name__ == "__main__":
    generate_customer_intelligence_data()
